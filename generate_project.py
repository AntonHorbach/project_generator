import os
import sys
import subprocess
import shutil
import xml.etree.ElementTree


def processNode(node, prj_path, template_dir_path):
    for item in node:
        item_type = item.attrib['type']

        if item_type == 'folder':
            processFolderNode(item, prj_path, template_dir_path)
        elif item_type == 'file':
            processFileNode(item, prj_path, template_dir_path)
        else:
            print("Unknown item type")
            exit(1)


def processFileNode(node, prj_path, template_dir_path):
    generator = node.find('generator')

    if generator:
        processGeneratorNode(generator, prj_path, template_dir_path)
        return

    file_name = node.attrib['name']
    file_data = node.find('data').text

    if not file_data:
        file_data = ""

    if file_data != '@default@':
        file = open(prj_path + file_name, 'w+')
        file.write(file_data)
        file.close()
    else:
        shutil.copy('./defaults/' + file_name, prj_path)


def processGeneratorNode(node, prj_path, template_dir_path):
    tool_name = node.find('tool_name').text
    args = []

    for arg in node.iter('arg'):
        args.append(arg.text)

    if tool_name == 'copy-paste':
        shutil.copy(template_dir_path + '/' + args[0], prj_path)
    else:
        subprocess.run([tool_name] + args)


def processFolderNode(node, prj_path, template_dir_path):
    folder_path = prj_path + node.attrib['name'] + '/'
    os.makedirs(folder_path, exist_ok=True)

    processNode(node, folder_path, template_dir_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_project.py [PATH_TO_PROJECT_TEMPLATE] [PATH_TO_PROJECT]")
        exit(1)

    prj_template_file = open(sys.argv[1])

    if not prj_template_file:
        print("Can't open file by such path")
        exit(1)

    path_to_prj_folder = sys.argv[2] + '/'

    os.makedirs(path_to_prj_folder, exist_ok=True)

    prj_template_dom = xml.etree.ElementTree.parse(prj_template_file)
    prj_tree_node = prj_template_dom.getroot()

    processNode(prj_tree_node, path_to_prj_folder, os.path.dirname(sys.argv[1]))
