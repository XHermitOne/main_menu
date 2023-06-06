#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main linux terminal menu.

Use:

main_menu [options]

Options:
    --help|-h|-?    Program help
    --version|-v    Program version
    --log|-l        Log mode
    --settings=     Settings filename

Format settings file:
[PALETTE]           -   palette section
[MAIN_MENU]         -   main section
    description     -   menu item description
    label           -   menu item label
    children        -   menu item child names
    cmd001..cmd999  -   command sequense
"""

import sys
import os
import os.path
# import platform
import getopt

try:
    import configparser
except ImportError:
    print('Import error configparser')

try:
    import cursesmenu
    import cursesmenu.items
except ImportError:
    print(u'Import error. Not found curses-menu library')
    print(u'For install: pip3 install curses-menu')
    sys.exit(2)

__version__ = (0, 0, 1, 1)

LOG_MODE = False
SETTINGS_FILENAME = 'main_menu.ini'
DEFAULT_ENCODING = 'utf-8'

MAIN_MENU = None


def INI2Dict(ini_filename):
    """
    Presentation of the contents of an INI file as a dictionary.

    :type ini_filename: C{string}
    :param ini_filename: Full name of the settings file.
    :return: Filled dictionary or None in case of error.
    """
    ini_file = None
    try:
        if not os.path.exists(ini_filename):
            print(u'INI file <%s> not found' % ini_filename)
            return None
            
        ini_parser = configparser.ConfigParser()
        ini_file = open(ini_filename, 'rt', encoding=DEFAULT_ENCODING)
        ini_parser.read_file(ini_file)
        ini_file.close()
        
        ini_dict = {}
        sections = ini_parser.sections()
        for section in sections:
            params = ini_parser.options(section)
            ini_dict[section] = {}
            for param in params:
                param_str = ini_parser.get(section, param)
                try:
                    # Perhaps in the form of a parameter is recorded a dictionary / list / None / number, etc.
                    param_value = eval(param_str)
                except:
                    # No, it's a string.
                    param_value = param_str

                ini_dict[section][param] = param_value
        
        return ini_dict
    except:
        if ini_file:
            ini_file.close()
        print(u'Error converting INI file <%s> to dictionary' % ini_filename)
        # raise
    return None


def buildMenuItem(settings, name=None, parent_menu=None):
    """
    Build menu item object.

    :param settings: Settings data dictiionary.
    :param name: Current item name.
    :param parent_menu: Parent menu.
    :return: Menu object.
    """
    section = settings.get(name, dict())
    label = section.get('label', 'unknown')
    children_names = section.get('children', None)
    # print(u'Create <%s>' % label)

    if children_names:
        menu = buildMenu(settings, name=name)
        menu_item = cursesmenu.items.SubmenuItem(label, submenu=menu, menu=parent_menu)
    else:
        cmd_options = [option for option in section.keys() if option.startswith('cmd')]
        cmd_options.sort()
        commands = [section[option] for option in cmd_options]
        command = '; '.join(commands)
        menu_item = cursesmenu.items.CommandItem(label, command=command)
    return menu_item


def buildMenu(settings, name=None, parent_menu=None):
    """
    Build menu object.
    
    :param settings: Settings data dictiionary.
    :param name: Current item name.
    :param parent_menu: Parent menu.
    :return: Menu object.
    """
    if name is None:
        name = 'MAIN_MENU'

    section = settings.get(name, dict())
    label = section.get('label', 'unknown')
    children_names = section.get('children', None)

    if parent_menu is None:
        parent_menu = cursesmenu.CursesMenu(label)

    if children_names:
        for child_name in children_names:
            menu_item = buildMenuItem(settings, name=child_name, parent_menu=parent_menu)
            parent_menu.items.append(menu_item)
    else:
        menu_item = buildMenuItem(settings, name=name, parent_menu=parent_menu)
        parent_menu.items.append(menu_item)
    return parent_menu


def main(*argv):
    """
    Main function.

    @param argv: Command line options.
    """
    global LOG_MODE
    global SETTINGS_FILENAME

    try:
        options, args = getopt.getopt(argv, 'h?vl',
                                      ['help', 'version', 'log',
                                       'settings='])
    except getopt.error as msg:
        print(str(msg))
        print(__doc__)
        sys.exit(2)

    for option, arg in options:
        if option in ('-h', '--help', '-?'):
            print(__doc__)
            sys.exit(0)
        elif option in ('-v', '--version'):
            txt_version = '.'.join([str(ver) for ver in __version__])
            print(u'Version: %s' % txt_version)
            sys.exit(0)
        elif option in ('-l', '--log'):
            LOG_MODE = True
        elif option == '--settings':
            SETTINGS_FILENAME = arg

    global MAIN_MENU
    settings = INI2Dict(SETTINGS_FILENAME)
    MAIN_MENU = buildMenu(settings)

    MAIN_MENU.start()
    _ = MAIN_MENU.join()


if __name__ == '__main__':
    main(*sys.argv[1:])
