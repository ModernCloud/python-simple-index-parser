import os
import re
from urllib.request import urlretrieve, urlopen
from progress.bar import Bar


class Parser:
    def __init__(self, main_url, base_path):
        self.main_progress = Bar('Steps', max=5)
        self.main_url = main_url
        self.main_file = f'{base_path}/simple_index.html'
        self.base_path = base_path
        self.link_pattern = re.compile('<a href="(.+?)">(.+?)</a>')
        self.output_file = open(f'{base_path}/package_version.sql', 'a+', buffering=100)
        open(f'{base_path}/last_index', 'a').close()
        self.last_index = open(f'{base_path}/last_index', 'r+')

    def run(self):
        self.download_main_file()
        self.extract_packages()
        self.output_file.close()

    def download_main_file(self):
        if os.path.isfile(self.main_file) is False:
            urlretrieve(self.main_url + '/simple', self.main_file)
        self.main_progress.next()

    def extract_packages(self):
        last_index = self.get_last_index()
        keyboard_interrupt = False
        self.main_progress.next()
        with open(self.main_file, 'r') as reader:
            self.main_progress.next()
            links = re.findall(self.link_pattern, reader.read())
            self.main_progress.next()
            packages_progress = Bar('Packages', index=last_index, max=len(links))
            for index, value in enumerate(links[last_index:]):
                try:
                    package_name = value[1]
                    package_link = self.main_url + value[0]
                    versions = self.extract_package(package_link)
                    self.write_output(package_name, versions)
                    self.update_last_index(last_index + index)
                    packages_progress.next()
                    if keyboard_interrupt:
                        break
                except KeyboardInterrupt:
                    keyboard_interrupt = True
            packages_progress.finish()
            self.main_progress.next()

    def extract_package(self, package_link):
        versions = []
        details = self.download_link(package_link)
        links = re.findall(self.link_pattern, details.decode('utf-8'))
        for version_link, package_version in links:
            if package_version.find('.tar.gz') > -1:
                versions.append(package_version.replace('.tar.gz', '').split('-')[-1])
        return versions

    def get_last_index(self):
        last_index = self.last_index.read()
        if last_index == '':
            last_index = 0
        last_index = int(last_index)
        return last_index

    def update_last_index(self, current_index):
        self.last_index.seek(0)
        self.last_index.write(str(current_index))

    @staticmethod
    def download_link(package_link):
        with urlopen(package_link) as response:
            return response.read()

    def write_output(self, package_name, versions):
        if len(versions) == 0:
            return
        values = []
        for version in versions:
            values.append(f'("{package_name}", "{version}")')
        sql = f'INSERT IGNORE INTO python_package (name, version) VALUES {",".join(values)};\n'
        self.output_file.write(sql)


if __name__ == '__main__':
    Parser(
        main_url='https://pypi.org',
        base_path=os.path.dirname(os.path.realpath(__file__))
    ).run()
