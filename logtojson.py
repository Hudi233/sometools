import json
import pymysql
from datetime import datetime
def get_info(key_id,gitdepartment):
        conn = pymysql.connect(
                host = 'x.x.x.x',
                port = 3306,
                user = 'xxx',
                password = 'xxx',
                database = 'gitlab'
                )
        cursor = conn.cursor()
        #get user_id
        sql = "SELECT user_id FROM gitlabkey WHERE id=" + str(key_id)
        cursor.execute(sql)
        row_1 = cursor.fetchone()

        if row_1 != None:
                user_id = row_1[0]
                #get name_username
                sql2 = "SELECT name,username FROM gitlabuser WHERE id=" + str(user_id)
                cursor.execute(sql2)
                row_2 = cursor.fetchone()
                name_username = row_2
                #get user_department
                sql3 = "SELECT ldap FROM userdepartment WHERE id=" + str(user_id)
                cursor.execute(sql3)
                row_3 = cursor.fetchone()
                if row_3 != None:
                        userdepartment = row_3[0].split(",")[1]
                else:
                        userdepartment = 'null'
                user_department = userdepartment
        else:
                name_username = {'null','null'}

        #get group_department
        sql4 = "SELECT git_department FROM gitlabdepartment WHERE git_group='" + str(gitdepartment) + "'"
        cursor.execute(sql4)
        row_4 = cursor.fetchone()
        if row_4 != None:
                groupdepartment = row_4[0]
        else:
                groupdepartment = "probably not a group"
        return (name_username,user_department,groupdepartment)

def logtojson():
        with open(r'/opt/gitlablog/gitlab-shell.log') as myfile:
                logs = myfile.readlines()
                array = []
                for log in logs:
                        array.append(log)
        logdict = []
        for i in range(len(array)):
                info = array[i]
                info1 = info.split()
                tyr:
                        if info1[0] == "I," and info1[6] == "gitlab-shell:":
                                time1 = info1[1].split("[")[1]
                                time = time1.split(".")[0]
                                gitcommand = info1[10].split("<")[1]
                                gitpath = info1[11].split(">")[0]
                                key = info1[16].split("-")[1]
                                key_id = key.split(".")[0]
                                group = gitpath.split("/")[5]
                                info = get_info(key_id,group)
                                name = info[0][0]
                                username = info[0][1]
                                user_department = info[1]
                                groupdepartment = info[2]

                                newlog = {
                                        "logDate": time,
                                        "gitcommand":gitcommand,
                                        "gitpath":gitpath,
                                        "group-department":groupdepartment,
                                        "name":name,
                                        "username":username,
                                        "user_department":user_department,
                                        "key_id":key_id
                                        }
                                logdict.append(newlog)
                except IndexError as e:
                        print info 

        with open(datetime.now().date().isoformat()+'.log',"w") as f:
                for i in logdict:
                        json.dump(i,f,ensure_ascii=False)
                        f.write('\n')

if __name__ == '__main__':
        logtojson()

try:
        pass
except Exception as e:
        raise e