# -*- coding: UTF-8 -*-
import gitlab
class GitlabAPI(object):
    def __init__(self, token):
        self.gl = gitlab.Gitlab('https://gitlab.gz.cvte.cn', private_token=token)
    
    def get_user_id(self, username):
        user = self.gl.users.list(username=username)[0]
        return user.id

    # path与name可以不同, 但full_path体现在网页url上, 能够唯一访问一个group
    def get_group_id(self, grouppath):
        groups = self.gl.groups.list(search=grouppath)
        for i in groups:
            if i.full_path == grouppath:
                gid = i.id
        return gid

    # 允许path与name不相同, path可以在settings中修改, path_with_namespace体现在网页url上, 能够唯一访问一个project
    def get_project_id(self, projectpath):
        print(projectpath)
        projects = self.gl.projects.list(search=projectpath.split('/')[0])
        print(projects)
        pid = ''
        for project in projects:
            print('-----------------------------')
            print(project.id)
            tmp = self.get_project(project.id)
            print(tmp.path_with_namespace)
            if str(project.path_with_namespace).strip() == projectpath.lower():
                print(project.id)
                return project.id
        return None
    
    def get_project_path(self, pid):
        project = self.gl.projects.get(pid)
        return project.path_with_namespace
    
    # 使用场景: 通过xml的group path获得gid, group id是一个unique属性
    def get_group(self, gid):
        group = self.gl.groups.get(gid)
        return group
    
    # 返回project对象
    def get_project(self, pid):
        project = self.gl.projects.get(pid)
        return project
    
    def __get_user(self, uid):
        user = self.gl.users.get(uid)
        return user
    
    def get_project_members(self, pid):
        project = self.get_project(pid)
        members = project.members.all(all = True)
        return members
    
    def is_gitlab_account(self, account):
        # by username
        if len(self.gl.users.list(username=account)) == 0:
            return False
        user = self.gl.users.list(username=account)[0]
        print(user.name)
        return True
    
    def is_project_menber(self, uid, pid):
        project = self.get_project(pid)
        members = project.members.all(all=True)
        user = self.__get_user(uid)
        if user in members:
            return True
        else:
            return False
    
    # 为一个project设置一个用户权限
    def add_project_member(self, uid, pid, access_level):
        project = self.get_project(pid)
        if access_level == 'guest':
            member = project.members.create({'user_id': uid, 'access_level':
                gitlab.GUEST_ACCESS})
        elif access_level == 'reporter':
            member = project.members.create({'user_id': uid, 'access_level':
                gitlab.REPORTER_ACCESS})
        elif access_level == 'developer':
            member = project.members.create({'user_id': uid, 'access_level':
                gitlab.DEVELOPER_ACCESS})
        elif access_level == 'maintainer':
            member = project.members.create({'user_id': uid, 'access_level':
            gitlab.MAINTAINER_ACCESS})
        else:
            print('Error access level!!! Exit when setting access!!!')
            return False
        return True
    
    def modify_user_access(self, uid, pid, access_level):
        project = self.get_project(pid)
        member = project.members.get(uid)
        if access_level == 'guest':
            member.access_level = gitlab.GUEST_ACCESS
        elif access_level == 'reporter':
            member.access_level = gitlab.REPORTER_ACCESS
        elif access_level == 'developer':
            member.access_level = gitlab.DEVELOPER_ACCESS
        elif access_level == 'maintainer':
            member.access_level = gitlab.MAINTAINER_ACCESS
        else:
            print('Error access level!!! Exit when setting access!!!')
            return False
        member.save()
        return True
    
    def delete__project_member(self, uid, pid):
        project = self.get_project(pid)
        project.members.delete(uid)

if __name__ == '__main__':
    account = 'zhouweihao'
    git = GitlabAPI('Y8-wVCBS2Wzush7p38xv')
    project = git.get_project(29177)
    print(project)
    print(''.join(project.name_with_namespace.split()))
    pid = git.get_project_id('9950/Android')
