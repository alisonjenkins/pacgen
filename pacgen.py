#!/usr/bin/env python
"""
This program is used to generate and aid in the maintenance of ATLauncher
Minecraft mod packs.
"""
import xml.etree.ElementTree as ET
import urllib2
import json

MINECRAFT_VERSION = '1.6.4'
BOT_URL = "http://bot.notenoughmods.com/%s.json" % MINECRAFT_VERSION


class Pacgen(object):
    def get_bot_mods(self):
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36"
        request = urllib2.Request(BOT_URL, headers=headers)
        BOT_MODS_RESPONSE = urllib2.urlopen(request)
        self.BOT_MOD_LIST = json.loads(BOT_MODS_RESPONSE.read())

    def find_mod_version(self, bot_mod_list, mod_name):
        """
        This function searches through the notenoughmods bot's mod list
        for the specified mod name. If found it returns the bot's mod entry
        else returns None.
        """
        for bot_mod in bot_mod_list:
            if bot_mod['name'].lower() == mod_name.lower():
                return bot_mod
        return None

    def parse_pack_xml(self, xml_path="../pack.xml"):
        """
        Parses the XML and populates the PACK_XML_TREE and
        PACK_XML_ROOT instance variables.
        """
        self.PACK_XML_TREE = ET.parse(xml_path)
        self.PACK_XML_ROOT = self.PACK_XML_TREE.getroot()

    def generate_pack_report(self, type="versions"):
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
            for mod in self.PACK_XML_ROOT[2]:
                current_version = self.find_mod_version(self.BOT_MOD_LIST,
                                                        mod.attrib['name'])
                mod_version_no_mc = \
                    mod.attrib['version'].replace('%s-'
                                                  % MINECRAFT_VERSION, '')

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
                        PACK_REPORT_HTML += """<tr>
                                                 <td>
                                                   <a href=\"%s\">%s</a>
                                                 </td>""" \
                            % (mod.attrib['website'], mod.attrib['name'])
                        if current_version['longurl'] != "Unknown":
                            PACK_REPORT_HTML += """<td>
                                                     <a href=%s>Update</a>
                                                   </td>"""\
                                % current_version['longurl']
                        else:
                            PACK_REPORT_HTML += "<td></td>"
                        PACK_REPORT_HTML += "<td>%s</td><td>%s</td></tr>"\
                            % (mod.attrib['version'], current_version['dev'])
                else:
                    if current_version['version'] != mod_version_no_mc:
                        PACK_REPORT_HTML += """<tr>
                                               <td>
                                                 <a href=\"%s\">%s</a>
                                               </td>"""\
                            % (mod.attrib['website'], mod.attrib['name'])
                        if current_version['longurl'] != "Unknown":
                            PACK_REPORT_HTML += """<td>
                                                   <a href=%s>Update</a>
                                                 </td>"""\
                                % current_version['longurl']
                        else:
                            PACK_REPORT_HTML += "<td></td>"
                        PACK_REPORT_HTML += "<td>%s</td><td>%s</td></tr>"\
                            % (mod.attrib['version'],
                                current_version['version'])
                # except:
                #     print(mod.attrib['name'])

            PACK_REPORT_HTML += "</table></body></html>"
            linksfile.write(PACK_REPORT_HTML)

if __name__ == "__main__":
    pg = Pacgen()
    pg.get_bot_mods()  # get current versions of mods from notenoughmods bot
    pg.parse_pack_xml()  # parse the current version of the pack's xml
    # generate a report showing the current and latest
    # (according to notenoughmods) versions.
    pg.generate_pack_report()
