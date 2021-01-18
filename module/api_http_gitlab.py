import requests
import urllib3
import json

urllib3.disable_warnings()
# token ='Y8-wVCBS2Wzush7p38xv'
# 'https://gitlab.gz.cvte.cn/api/v4'

class GitlabAPI(object):
    def __init__(self, url, token):
        self.http_url = url
        self.http_token = {"PRIVATE-TOKEN": token}

    def get(self, option, data={}, headers={}):
        try:
            headers.update(self.http_token)
            ret = requests.get(
                url=self.http_url + option,
                data=data,
                headers=headers,
                proxies=None,
                verify=False
            )
            return json.loads(ret.text)
        except requests.HTTPError as e:
            raise e

    def post(self, option, data={}, headers={}):
        try:
            headers.update(self.http_token)
            ret = requests.post(
                url=self.http_url + option,
                data=data,
                headers=headers,
                proxies=None,
                verify=False
            )
            return json.loads(ret.text)
        except requests.HTTPError as e:
            print(e)
            raise e

    def put(self, option, data={}, headers={}):
        try:
            headers.update(self.http_token)
            ret = requests.put(
                url=self.http_url + option,
                data=data,
                headers=headers,
                proxies=None,
                verify=False
            )
            return json.loads(ret.text)
        except requests.HTTPError as e:
            raise e

    def delete(self, option, data={}, headers={}):
        try:
            headers.update(self.http_token)
            ret = requests.delete(
                url=self.http_url + option,
                headers=headers,
                proxies=None,
                verify=False
            )
            return json.loads(ret.text)
        except requests.HTTPError as e:
            print(e)
            raise e

    def lockBranch(self, pid, branchName="", push_access_level=0, merge_access_level=40):
        """
        Modify push or merge level of a protected branch
        :param pid: project id
        :param branchName: branch
        :param push_access_level: push level of protected branch
        :param merge_access_level: merge level of protected branch
        :return: None
        """
        print(str(pid) + ": " + branchName)
        sub_url = "/projects/" + str(pid) + "/protected_branches"
        data = {
            'name': branchName,
            'push_access_level': push_access_level,
            'merge_access_level': merge_access_level
        }
        ret = self.post(sub_url, data)
        print(ret.status_code)

    def deleteBranch(self, pid, branch):
        """
        Delete project branch.
        :param pid: project id
        :param branch: branch to be deleted
        :return: None
        """
        sub_url = "/projects/" + str(pid) + "/protected_branches/" + branch
        ret = self.delete(sub_url)
        print(ret)

    def getProjectIdByPath(self, path):
        """
        Query project id by project path with namespace.
        :param path: project path with namespace
        :return: project id
        """
        sub_url = "/projects/" + path.replace('/', "%2F")
        ret = self.get(sub_url)
        print(ret['id'])
        return ret['id']
    
    def getProjectPathById(self, id):
        """
        Query project id by project path with namespace.
        :param path: project path with namespace
        :return: project id
        """
        sub_url = "/projects/" + str(id)
        ret = self.get(sub_url)
        print(ret['path_with_namespace'])
        return ret['path_with_namespace']
    
    def getUserIdByUsername(self, username):
        """
        Query user id by username.
        :param username: username
        :return: user id
        """
        params = {
            "username": username,
            "state": "active"
        }
        ret = self.get("/users", params)
        print(ret[0])
        return ret[0]['id']
    
    def getProjectUsers(self, id):
        """
        Query project members by project id.
        :param id: project id
        :return: users list
        """
        sub_url = "/projects/" + str(id) + "/users?per_page=200"
        ret = self.get(sub_url)
        return ret
    
    def addMemberToProject(self, uid, pid, access_level):
        """
        Add a member to a project.
        :param uid: user id
        :param pid: project id
        :param access_level: user access level
        :return: None
        """
        params = {
            'user_id': uid,
            'access_level': access_level
        }
        sub_url = "/projects/" + str(pid) + "/members"
        ret = self.post(sub_url, data=params)
        return ret
    
    def addMemberToGroup(self, uid, gid, access_level):
        """
        Add a member to a group.
        :param uid: user id
        :param gid: group id
        :param access_level: user access level
        :return: None
        """
        params = {
            'user_id': uid,
            'access_level': access_level
        }
        sub_url = "/groups/" + str(gid) + "/members"
        ret = self.post(sub_url, data=params)
        return ret

    def editMemberToProject(self, uid, pid, access_level):
        """
        Edit member access level of a project.
        :param uid: user id
        :param pid: project id
        :param access_level: user access level
        :return: None
        """
        params = {
            'access_level': access_level
        }
        sub_url = "/projects/" + str(pid) + "/members/" + str(uid) + "?access_level=" + str(access_level)
        ret = self.put(sub_url)
        return ret

    def editMemberToGroup(self, uid, gid, access_level):
        """
        Edit member access level of a group.
        :param uid: user id
        :param gid: group id
        :param access_level: user access level
        :return: None
        """
        params = {
            'access_level': access_level
        }
        sub_url = "/groups/" + str(gid) + "/members" + str(uid)
        ret = self.put(sub_url, data=params)
        return ret
    
    def listProjectMembers(self, pid):
        """
        List all members including inherited members of a project.
        :param pid:
        :return: members list
        """
        sub_url = "/projects/" + str(pid) + "/members/all?per_page=200"
        ret = self.get(sub_url)
        return ret
    
    def isProjectMember(self, username, pid):
        """
        Query whether user is member of a project.
        :param username: username
        :param pid: project id
        :return: Boolean
        """
        userList = str(self.listProjectMembers(pid))
        if username in userList:
            return True
        else:
            return False

    def getUserStatus(self, username):
        """
        Query whether user exist or not by query user status with username.
        :param username: username
        :return: Boolean (existence)
        """
        sub_url = "/users/" + str(username) + "/status"
        ret = self.get(sub_url)
        if "404" in str(ret):
            return False
        else:
            return True
        

if __name__ == '__main__':
    token = 'Y8-wVCBS2Wzush7p38xv'
    url = 'https://gitlab.gz.cvte.cn/api/v4'
    git = GitlabAPI(url, token)
    pid = git.getProjectIdByPath('seewosystem/3399_9')
    uid = git.getUserIdByUsername('laiyuansheng')
    if git.isProjectMember('laiyuansheng', pid):
        print(git.editMemberToProject(uid, pid, 20))
    else:
        print(git.addMemberToProject(uid, pid, 30))
    
    path = git.getProjectPathById(45050)