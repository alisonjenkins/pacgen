#!/usr/bin/env python
"""
This program is used to generate and aid in the maintenance of ATLauncher
Minecraft mod packs.
"""
import xml.etree.ElementTree as ET
import urllib2
import json
import pdb

MINECRAFT_VERSION = '1.6.4'
BOT_URL = "http://bot.notenoughmods.com/%s.json" % MINECRAFT_VERSION


def get_bot_mods():
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36"
    request = urllib2.Request(BOT_URL, headers=headers)
    BOT_MODS_RESPONSE = urllib2.urlopen(request)
    BOT_MOD_LIST = json.loads(BOT_MODS_RESPONSE.read())
    return BOT_MOD_LIST


def find_mod_version(bot_mod_list, mod_name):
    """
    This function searches through the notenoughmods bot's mod list
    for the specified mod name. If found it returns the bot's mod entry
    else returns None.
    """
    for bot_mod in bot_mod_list:
        if bot_mod['name'].lower() == mod_name.lower():
            return bot_mod
    return None


BOT_MOD_LIST = get_bot_mods()
PACK_XML_TREE = ET.parse('../pack.xml')
PACK_XML_ROOT = PACK_XML_TREE.getroot()
with open('../pacgen_report.html', 'w') as linksfile:
    PACK_REPORT_HTML = """<html>
    <body>
    <table>
    <tr>
    <th>Site link</th>
    <th>Update link</th>
    <th>XML version</th>
    <th>Current Version</th>
    </tr>"""
    for mod in PACK_XML_ROOT[2]:
        current_version = find_mod_version(BOT_MOD_LIST, mod.attrib['name'])
        mod_version_no_mc = \
            mod.attrib['version'].replace('%s-'
                                          % MINECRAFT_VERSION, '')

        # pdb.set_trace()
        # try:
        if not current_version:
            current_version = {}
            current_version['version'] = "Unknown"
            current_version['longurl'] = "Unknown"
            mod_version_no_mc = \
                mod.attrib['version'].replace('%s-'
                                              % MINECRAFT_VERSION, '')
        if current_version['version'] == 'dev-only':
            if current_version['dev'] != mod_version_no_mc:
                PACK_REPORT_HTML += "<tr><td><a href=\"%s\">%s</a></td>" \
                    % (mod.attrib['website'], mod.attrib['name'])
                if current_version['longurl'] != "Unknown":
                    PACK_REPORT_HTML += "<td><a href=%s>Update</a></td>"\
                        % current_version['longurl']
                else:
                    PACK_REPORT_HTML += "<td></td>"
                PACK_REPORT_HTML += "<td>%s</td><td>%s</td></tr>"\
                    % (mod.attrib['version'], current_version['dev'])
        else:
            if current_version['version'] != mod_version_no_mc:
                PACK_REPORT_HTML += "<tr><td><a href=\"%s\">%s</a></td>"\
                    % (mod.attrib['website'], mod.attrib['name'])
                if current_version['longurl'] != "Unknown":
                    PACK_REPORT_HTML += "<td><a href=%s>Update</a></td>"\
                        % current_version['longurl']
                else:
                    PACK_REPORT_HTML += "<td></td>"
                PACK_REPORT_HTML += "<td>%s</td><td>%s</td></tr>"\
                    % (mod.attrib['version'], current_version['version'])
        # except:
        #     print(mod.attrib['name'])

    PACK_REPORT_HTML += "</table></body></html>"
    linksfile.write(PACK_REPORT_HTML)
