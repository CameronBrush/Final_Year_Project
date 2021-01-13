from bs4 import BeautifulSoup
import re
import os
import ntpath
import json
from application.parsers.markdown_processor import process_markdown
from application.models.gauge_data_models import Scenario, Concept, ClientObjects


class gauge_parser:
    def parse_cpt(self, filepath):
        with open(filepath, encoding="utf-8") as file:
            markdown_string = file.read()
            html = process_markdown(markdown_string)
            soup = BeautifulSoup(html, "html.parser")
            cpt_names = list(soup.findAll('h1'))
            steps = list(soup.findAll('ul'))
            concepts = list()
            for i in range(len(cpt_names)):
                name = cpt_names[i].get_text()
                cpt_steps = list()
                client_side = "null"
                for step in steps[i].findAll('li'):
                    if("http" in step.get_text()):
                        client_side = step.get_text()
                    if("http" not in step.get_text()):
                        cpt_steps.append(step.get_text())
                concept = Concept(name = name, steps=cpt_steps, client=client_side)
                concepts.append(concept)
            return concepts

    def parse_spec(self, filepath):
        with open(filepath, encoding="utf-8") as file:
            filename = ntpath.basename(filepath)
            markdown_string = file.read()
            html = process_markdown(markdown_string)
            print(html)
            soup = BeautifulSoup(html, 'html.parser')
            spec_name = soup.find('h1').get_text()
            spec_name = re.sub(r'[^\w\s]', '', spec_name)
            scenario_titles = list(soup.findAll('h2'))
            steps = list(soup.findAll('ul'))
            scenarios = list()
            # Checking if there are any before steps
            if len(scenario_titles) != len(steps):
                scenario_steps = list()
                for step in steps[0].findAll('li'):
                    step_text = step.get_text()
                    scenario_steps.append(step_text)
                scenario = Scenario(name=f"Prerequisite {spec_name}", steps=scenario_steps, source_file=filename)
                scenarios.append(scenario)
                steps = steps[1:]
            for i in range(len(scenario_titles)):
                title = scenario_titles[i].get_text()
                scenario_steps = list()
                client_side = "null"
                for step in steps[i].findAll('li'):
                    step_text = step.get_text()
                    if("http" in step_text):
                         print(step_text)
                         client_side = step_text
                    if("http" not in step_text):
                     scenario_steps.append(step_text)
                scenario = Scenario(name = title, steps=scenario_steps, client=client_side, source_file=filename)
                scenarios.append(scenario)
                print(scenarios)
            return scenarios

    def parse_resource(self, filepath):
        with open(filepath) as f:
            j = json.load(f)
            keys = list()
            values = list()
            for x in j:
                keys.append(x['key']);
                values.append((x["value"]))
            clientObjects = ClientObjects(keys=keys,values=values)
        return clientObjects


if __name__ == "__main__":
    filepath = r"C:\Users\camer\Documents\GaugeDepend\samples_test_suites\GmailGaugeTestSuite\src\test\resources\elementValues\HomePage.json"
    parser = gauge_parser()
    test = parser.parse_resource(filepath)
#     for subdir, dirs, files in os.walk(filepath):
#         for file in files:
#             path = subdir + os.sep + file
#             try:
#                 with open(path) as file:
#                     m_str = file.read()
#                     process_markdown(m_str)
#
#             except:
#                 print(f"Error processing {file}")
#     path = r"C:\Users\camer\Documents\GaugeDepend\samples_test_suites\GmailGaugeTestSuite\specs\petclinc\HomePage.spec"
#     parser = gauge_parser()
#     scenarios = parser.parse_spec(path)
#     print(len(scenarios))
