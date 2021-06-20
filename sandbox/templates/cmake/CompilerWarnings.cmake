function(set_warnings warnings_lib_name)

    set(WARNINGS
            -Wall
            -Wextra
            -Wshadow
            -Wnon-virtual-dtor
            -Wold-style-cast
            -Wcast-align
            -Wunused
            -Woverloaded-virtual
            -Wpedantic
            -Wconversion
            -Wsign-conversion
            -Wnull-dereference
            -Wdouble-promotion
            -Wformat=2)

    if (WARNINGS_AS_ERRORS)
        set(WARNINGS ${WARNINGS} -Werror)
    endif ()

    if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        set(WARNINGS
                ${WARNINGS}
                -Wmisleading-indentation
                -Wduplicated-cond
                -Wduplicated-branches
                -Wlogical-op
                -Wuseless-cast)
    endif ()

    target_compile_options(${warnings_lib_name} INTERFACE ${WARNINGS})

endfunction()