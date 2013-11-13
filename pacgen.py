#!/usr/bin/env python
"""
This program is used to generate and aid in the maintenance of ATLauncher
Minecraft mod packs.
"""
import xml.etree.ElementTree as ET
import urllib2
import sys
import json
import pdb

try:
    import yaml
except ImportError:
    print("Failed to import pyyaml please install pyyaml")
    sys.exit(1)


class Pacgen(object):
    def __init__(self, config_file_path="../pacgen_config.yaml"):
        self.parse_config_file(config_file_path)
        self.MINECRAFT_VERSION = self.config['minecraft-version']
        self.BOT_URL = "http://bot.notenoughmods.com/%s.json"\
            % self.MINECRAFT_VERSION

    def get_bot_mods(self):
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36"
        request = urllib2.Request(self.BOT_URL, headers=headers)
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

    def parse_config_file(self, config_path="../pacgen_config.yml"):
        with open(config_path) as config_file:
            config_contents = config_file.read()
        self.config = yaml.load(config_contents)

    def generate_missing_mods(self):
        self.missing_mods = []
        pack_mod_names = []
        for mod in self.PACK_XML_ROOT[2]:
            pack_mod_names.append(mod.attrib['name'])

        for mod in self.config['mods']:
            if mod['name'] not in pack_mod_names:
                 self.missing_mods.append(mod)

    def generate_outdated_mods(self):
        self.outdated_mods = []
        self.unknown_mods = []

        for mod in self.PACK_XML_ROOT[2]:
            current_version = self.find_mod_version(self.BOT_MOD_LIST,
                                                    mod.attrib['name'])
            mod_version_no_mc = \
                mod.attrib['version'].replace('%s-'
                                              % self.MINECRAFT_VERSION, '')

            if not current_version:
                self.unknown_mods.append(mod)
            elif current_version['version'] == 'dev-only':
                if current_version['dev'] != mod_version_no_mc:
                    self.outdated_mods.append(mod)
                    # if current_version['longurl'] != "Unknown":
                        # PACK_REPORT_HTML += """<td>
                        #                          <a href=%s>Update</a>
                        #                        </td>"""\
                        #     % current_version['longurl']
                    # else:
                    #     PACK_REPORT_HTML += "<td></td>"
                    # PACK_REPORT_HTML += "<td>%s</td><td>%s</td></tr>"\
                    #     % (mod.attrib['version'], current_version['dev'])
            else:
                if current_version['version'] != mod_version_no_mc:
                    self.outdated_mods.append(mod)
                    # PACK_REPORT_HTML += """<tr>
                    #                        <td>
                    #                          <a href=\"%s\">%s</a>
                    #                        </td>"""\
                    #     % (mod.attrib['website'], mod.attrib['name'])
                    # if current_version['longurl'] != "Unknown":
                    #     PACK_REPORT_HTML += """<td>
                    #                            <a href=%s>Update</a>
                    #                          </td>"""\
                    #         % current_version['longurl']
                    # else:
                    #     PACK_REPORT_HTML += "<td></td>"
                    # PACK_REPORT_HTML += "<td>%s</td><td>%s</td></tr>"\
                    #     % (mod.attrib['version'],
                    #         current_version['version'])

    def output_unknown_mods(self):
        html = ""
        if self.unknown_mods:
            html += """<h1>Unknown mods</h1>
            <table>
            <tr>
            <th>Site link</th>
            <th>Update link</th>
            </tr>"""

            for mod in self.unknown_mods:
                html += """
                <tr><td><a href=%s>%s</a></td><td><a href=%s>Update</a></tr>
                """ % (mod.attrib['website'], mod.attrib['name'], mod.attrib['website'])
            html += "</table>"

        return html

    def output_outdated_mods(self):
        html = ""

        if self.outdated_mods:
            html += """<h1>Outdated Mods</h1>
            <table>
            <tr>
            <th>Site link</th>
            <th>Update link</th>
            <th>XML version</th>
            <th>Current Version</th>
            </tr>"""

            for mod in self.outdated_mods:
                current_version = self.find_mod_version(self.BOT_MOD_LIST,
                                                        mod.attrib['name'])
                html += "<tr><td><a href=%s>%s</a></td><td><a href=%s>Update</a></td><td>%s</td><td>%s</td></tr>" % (mod.attrib['website'], mod.attrib['name'], current_version['longurl'], mod.attrib['version'], current_version['version'])

            html += "</table>"

        return html
            # for mod in self.PACK_XML_ROOT[2]:
            #     current_version = self.find_mod_version(self.BOT_MOD_LIST,
            #                                             mod.attrib['name'])
            #     mod_version_no_mc = \
            #         mod.attrib['version'].replace('%s-'
            #                                       % self.MINECRAFT_VERSION, '')

    def output_missing_mods(self):
        if self.missing_mods:
            html = """
            <h1>Missing Mods</h1>
            <table>
            <tr>
            <th>Missing Mod name</th>
            <th>Version requred</th>
            </tr>
            """

            for mod in self.missing_mods:
                html += """
                <tr>
                <td>%s</td>
                """ % mod['name']

                if 'version' in mod.keys():
                    html += """
                    <td>%s</td>
                    """ % mod['version']
                html += "</tr>"
            html += "</table>"
        else:
            html = ""

        return html

    def output_pack_report(self, type="versions"):
        # run report generating functions
        self.generate_missing_mods()
        self.generate_outdated_mods()

        with open('../pacgen_report.html', 'w') as linksfile:
            # create output html
            PACK_REPORT_HTML = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="utf-8" />
            </head>
            <body>
            """

            ## output any missing mods
            PACK_REPORT_HTML += self.output_missing_mods()
            ## output outdated and unknown mods
            PACK_REPORT_HTML += self.output_outdated_mods()
            ## output any unknown mods
            PACK_REPORT_HTML += self.output_unknown_mods()

            PACK_REPORT_HTML += "</html>"
            linksfile.write(PACK_REPORT_HTML)

if __name__ == "__main__":
    pg = Pacgen()
    pg.get_bot_mods()  # get current versions of mods from notenoughmods bot
    pg.parse_pack_xml()  # parse the current version of the pack's xml

    # generate a report showing the current and latest
    # (according to notenoughmods) versions.
    pg.output_pack_report()
