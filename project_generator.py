import os
import sys
import subprocess
import shutil
import xml.etree.ElementTree


def processNode(node, prj_path, tmpl_dir_path):
    for item in node:
        item_type = item.attrib['type']

        if item_type == 'folder':
            processFolderNode(item, prj_path, tmpl_dir_path)
        elif item_type == 'file':
            processFileNode(item, prj_path, tmpl_dir_path)
        else:
            print("Unknown item type")
            exit(1)


def processFileNode(node, prj_path, tmpl_dir_path):
    file_name = node.attrib['name']

    for action in node.iter('action'):
        processActionNode(action, prj_path, tmpl_dir_path, file_name)
        return

    file_data = node.find('data').text

    if not file_data:
        file_data = ""

    file = open(prj_path + file_name, 'w+')
    file.write(file_data)
    file.close()


def processActionNode(node, prj_path, tmpl_dir_path, src_file):
    action_name = node.find('action_name').text

    if action_name == 'copy-paste':
        processCopyPasteActionNode(node, prj_path, tmpl_dir_path)
    elif action_name == 'insert':
        processInsertActionNode(node, prj_path, src_file)
    else:
        args = []
        for arg in node.iter('arg'):
            args.append(arg.text)

        subprocess.run([action_name] + args)


def processCopyPasteActionNode(node, prj_path, tmpl_dir_path):
    to_copy = node.find('to_copy').text

    shutil.copy(tmpl_dir_path + to_copy, prj_path)


def processInsertActionNode(node, prj_path, file_to_insert):
    file_to_insert = prj_path + file_to_insert
    data_to_insert = node.find('to_insert').text
    search_by = 'forward'
    hint_to_insert = node.find('hint').text
    search_by_node = node.find('search_by')

    if search_by_node and search_by_node.text == "back":
        search_by = "back"

    file_lines = list(open(file_to_insert, 'r'))

    if search_by == "back":
        file_lines = reversed(file_lines)

    inserted = False

    for ind in range(len(file_lines)):
        if hint_to_insert in file_lines[ind]:
            file_lines.insert(ind, data_to_insert)
            inserted = True
            break

    if search_by == "back":
        file_lines = reversed(file_lines)

    if not inserted:
        file_lines.append(data_to_insert)

    with open(file_to_insert, 'w') as file:
        file.writelines(file_lines)


def processFolderNode(node, prj_path, tmpl_dir_path):
    folder_name = node.attrib['name'] + '/'

    for macro in macros_dictionary:
        if macro in folder_name:
            folder_name = folder_name.replace(macro, macros_dictionary[macro])
            break

    folder_path = prj_path + folder_name
    tmpl_dir_path = tmpl_dir_path + folder_name

    os.makedirs(folder_path, exist_ok=True)

    processNode(node, folder_path, tmpl_dir_path)


def getTemplateRoot(tmpl_file):
    if not tmpl_file:
        print("Can't open template file with such path")
        exit(1)

    tmpl_dom = xml.etree.ElementTree.parse(tmpl_file)

    return tmpl_dom.getroot()


def getTemplatePath(templates_dir, tmpl_name):
    templates_file = open(templates_dir + 'templates.xml')

    root = getTemplateRoot(templates_file)

    for template in root.iter('template'):
        if template.attrib['name'] == tmpl_name:
            return os.path.abspath(templates_dir + template.text)

    return ""


def getTemplatesFileNames(templates_dir):
    filenames = []
    templates_file = open(templates_dir + 'templates.xml')

    root = getTemplateRoot(templates_file)

    for template in root.iter('template'):
        filenames.append(os.path.abspath(templates_dir + template.text))

    return filenames


def processMacros(macros_dict):
    macros = macros_dict.keys()

    for root, dirs, files in os.walk(path_to_prj_folder):
        for file in files:
            file = root + '/' + file
            lines = []
            changed = False

            if file in templates_filenames:
                continue

            with open(file, "r") as f_in:
                for line in f_in:
                    for macro in macros:
                        if macro in line:
                            line = line.replace(macro, macros_dict[macro])
                            changed = True

                    lines.append(line)

            if changed:
                with open(file, "w") as f_out:
                    f_out.writelines(lines)


def getMacrosFromList(macros_list):
    macros_dict = {}

    for item in macros_list:
        (macro, value) = item.split('=')

        if not value:
            print("Bad argument " + item)
            exit(1)

        macros_dict['@' + macro + '@'] = value

    return macros_dict


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python3 project_generator.py"
            "[TEMPLATE_NAME] "
            "[PATH_TO_PROJECT_TEMPLATE_DIR] "
            "[PATH_TO_PROJECT] "
            "[(NOT_NECESSARY) MACROS (FOR EXAMPLE: ENTITY_NAME=ModuleName)]"
        )
        exit(1)

    template_name = sys.argv[1]

    template_dir_path = os.path.abspath(sys.argv[2]) + '/'
    template_file = open(getTemplatePath(template_dir_path, template_name))

    path_to_prj_folder = os.path.abspath(sys.argv[3]) + '/'
    os.makedirs(path_to_prj_folder, exist_ok=True)

    templates_filenames = getTemplatesFileNames(template_dir_path)
    macros_dictionary = {}

    if len(sys.argv) >= 5:
        macros_dictionary = getMacrosFromList(list(sys.argv[4::1]))

    tree_node = getTemplateRoot(template_file)

    processNode(tree_node, path_to_prj_folder, template_dir_path)

    template_file.close()

    if len(macros_dictionary.keys()) > 0:
        processMacros(macros_dictionary)

