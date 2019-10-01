"""
Basic Vsts GET operations using vsts APIs and python

Supports :

1. branches based on repo name
2. repo files based on path
3. file content based on file path

"""
import sys

import requests
from requests.auth import HTTPBasicAuth

if sys.version_info.major == 3:
    import urllib.parse as parser
else:
    import urllib as parser


class Vsts:

    def __init__(self, user_name=None, access_token=None):
        """

        :param user_name:
        :param access_token:
        """
        self.__user_name = user_name
        self.__access_token = access_token
        self.__api_url = "https://dev.azure.com/"
        self.__api_version = "5.1"

    @property
    def user_name(self):
        return self.__user_name

    @user_name.setter
    def user_name(self, user_name):
        self.__user_name = user_name

    @user_name.deleter
    def user_name(self):
        del self.__user_name

    @property
    def access_token(self):
        return self.__access_token

    @access_token.setter
    def access_token(self, access_token):
        self.__access_token = access_token

    @access_token.deleter
    def access_token(self):
        del self.__access_token

    @property
    def api_url(self):
        return self.__api_url

    @property
    def api_version(self):
        return self.__api_version

    def __invoke_api(self, extension=None, extra_headers=None):
        """

        :param extension:
        :param extra_headers:
        :return:
        """
        headers = {
            "Authorization": "Basic " + self.access_token,
            "Content-Type": "application/json"
        }
        url = self.api_url
        if extension:
            url += extension

        if extra_headers:
            headers = {**headers, **extra_headers}

        response = requests.get(url=url, headers=headers, auth=HTTPBasicAuth(self.user_name, self.access_token))

        return response

    @staticmethod
    def __format_repo(repo):
        """

        :param repo:
        :return:
        """
        data = repo.split("/")
        organization = data[0]
        repo_name = data[1]
        return organization, repo_name

    def get_branches(self, repo):
        """
        fetches branch names based on repo
        :param repo: string
        :return: array os strings
        """
        branches = []

        organization, repo_name = self.__format_repo(repo)

        extension = "{organization}/{repo_name}/_apis/git/repositories/{repo_name}/"
        extension += "refs?api-version={api_version}"
        extension = extension.format(organization=organization, repo_name=repo_name, api_version=self.__api_version)

        response = self.__invoke_api(extension=extension)

        if response.status_code == 200:
            response = response.json()

            for item in response["value"]:
                branch_name = item["name"].split("/")[-1]
                branches.append(branch_name)

            return branches
        else:
            return branches

    def fetch_content(self, repo, path, branch="master"):
        """
        fetches file names from the given path
        :param repo: string
        :param path: string
        :param branch: string
        :return: array of strings
        """
        files = []

        organization, repo_name = self.__format_repo(repo)

        path = parser.quote(path, safe="")

        extension = "{organization}/{repo_name}/_apis/git/repositories/{repo_name}/"
        extension += "items?scopePath={path}&version={branch}&recursionLevel=oneLevel&api-version={api_version}"
        extension = extension.format(organization=organization, repo_name=repo_name, path=path, branch=branch,
                                     api_version=self.__api_version)

        response = self.__invoke_api(extension=extension)

        if response.status_code == 200:
            response = response.json()

            for item in response["value"]:
                if item["gitObjectType"] == "blob":
                    file_path = item["path"].split("/")[-1]
                    file_path = parser.quote(file_path, safe="")
                    files.append(file_path)

            return files
        else:
            return files

    def read_file(self, repo, path, branch="master"):
        """
        fetches file content
        :param repo: string
        :param path: string
        :param branch: string
        :return: string
        """
        organization, repo_name = self.__format_repo(repo)

        path = parser.quote(path, safe="")

        extension = "{organization}/{repo_name}/_apis/git/repositories/{repo_name}/"
        extension += "items?path={path}&version={branch}&api-version={api_version}"
        extension = extension.format(organization=organization, repo_name=repo_name, path=path, branch=branch,
                                     api_version=self.__api_version)

        response = self.__invoke_api(extension=extension)

        if response.status_code == 200:
            response = response.content
            return response
        else:
            return response.json()


def main():
    """

    :return: None
    """
    vsts = Vsts(user_name="user_name", access_token="access_token")
    x = vsts.get_branches(repo="organization/repository")
    y = vsts.fetch_content(repo="organization/repository", path="/sub_dir", branch="branch")
    z = vsts.read_file(repo="organization/repository", path="/sub_dir/file_name.py", branch="branch")


if __name__ == "__main__":
    main()
