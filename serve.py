from flask import Flask, url_for, redirect

import requests, json, copy, dateparser, datetime, math
from html import escape
from lxml import html
import hmac, base64, hashlib
import re, flask
import json
# html templates
from html_templates import *

#Enter your own username and password for portal.mcpsmd.org
from config import *


def hash(password,contextdata):
    return hmac.new(contextdata.encode('ascii'), base64.b64encode(hashlib.md5(password.encode('ascii')).digest()).replace(b"=", b""), hashlib.md5).hexdigest()

class student:
    def __init__(self):
        self.url="https://portal.mcpsmd.org/guardian/home.html#/termGrades"
        self.s = requests.Session()
        self.grade = None
        self.schoolid = None
        self.studentnum = None
        self.studentid = None
        self.classes = None
        self.authenticated = False
        self.classgrades = {} 
        self.hypclasses = []
        self.upcount = 0
        self.grubmsg = ""
        return

    def getMP1Grades(self):
        mp1grades = {}
        for i in self.classes:
            if len(i) == 0:
                continue
            if i['termid'] == 'MP1':
                mp1grades[i['courseName']] = i['overallgrade']
        return mp1grades

    def authenticate(self, username, pw):
        result=self.s.get(self.url)
        tree = html.fromstring(result.text)
        pstoken = list(set(tree.xpath("//*[@id=\"LoginForm\"]/input[1]/@value")))[0]
        contextdata = list(set(tree.xpath("//input[@id=\"contextData\"]/@value")))[0]
        new_pw=hash(pw,contextdata)

        payload={
        'pstoken':pstoken,
        'contextData':contextdata,
        'dbpw':new_pw,
        'ldappassword':pw,
        'account':username,
        'pw':pw
        }
        p=self.s.post(self.url, data=payload)
        
        content = p.text
        self.schoolid = re.findall("root.schoolId = parseInt\('(.*)'\);", content)[0]
        self.studentid = re.findall("root.studentId = parseInt\('(.*)'\);", content)[0]
        self.studentnum = re.findall("root.studentNumber = parseInt\('(.*)'\);", content)[0]
        self.authenticated = True
        return

    def getClasses(self):
        baselink = 'https://portal.mcpsmd.org/guardian/prefs/gradeByCourseSecondary.json?schoolid=%s&student_number=%s&studentId=%s'%(self.schoolid, self.studentnum, self.studentid)
        classes = self.s.get(baselink)
        self.classes = json.loads(classes.text)
        #print(self.classes)

    def getAssignment(self, secid, termid="MP2"):
        baselink = 'https://portal.mcpsmd.org/guardian/prefs/assignmentGrade_AssignmentDetail.json?secid=%s&student_number=%s&schoolid=%s&termid=%s'%(secid, self.studentnum, self.schoolid, termid)
        assignments = self.s.get(baselink)
        #print(assignments.text)
        return json.loads(assignments.text)

    def getAssignments(self):
        for c in self.classes:
            try:
                if c['courseName'] == 'COUNSELOR' or c['courseName'] == 'HOMEROOM':
                    continue
                self.classgrades[c['courseName']] = self.getAssignment(c['sectionid'])
            except:
                pass
        #print(self.classgrades)


stu = student()
stu.authenticate(username, pw)
stu.getClasses()
stu.getAssignments()

dic = stu.classgrades

#mapping period to class
classmap = {}
for a in dic.keys():
    period = '??' + a
    for c in stu.classes:
        try:
            if c['courseName']==a and c['termid']=='MP2':
                period = c['period']
                break
        except:
            pass
    
    classmap[period] = a
print (classmap)
order = list(classmap.keys())
order.sort()


app = Flask(__name__)

@app.route('/')
def index():
    if 'stu' in globals() and stu.authenticated:
        return redirect(url_for('classes'))
    return redirect(url_for('login_func'))

@app.route('/login')
def login_func():
    return flask.render_template("login.html")

@app.route('/class')
def classes():
    # if student is not authenticated
    if 'stu' not in globals() or not stu.authenticated:
        # they aren't
        return redirect(url_for('login_func'))
    gradestoput = ""
    missingtoput = ""
    upcomingtoput = ""
    classdropdown = ""
    counter = 1
    c_missing = 1
    #Iterate through each class
    for num in order:
        missing = []
        info = copy.deepcopy(dic[classmap[num]])
        for i in stu.hypclasses:
            if classmap[num] == i[0]:
                info.append(i[1])
        names = []
        category = []
        duedate = []
        points = []
        possible = []
        #Print class name
        toprint = ""
        classname = classmap[num]
        misstoput = ""
        weights = {} #category name : [tuple of points + possible]
        #Iterate through each assignment
        hypid = 0
        for a in info:
            if len(a.keys()) == 0:
                continue
            if "hyp" in a:
                names.append(a["Description"] + " " + buttontemp.format(a["hyp"],a["hyp"]))
            else:
                names.append(a["Description"])
            category.append(a["AssignmentType"])
            duedate.append(a["DueDate"].split(" ")[0])
            points.append(a["Points"])
            possible.append(a["Possible"])

            

            if a["Points"] == "Z" or a["Points"] == "0.0":
                missing.append([classmap[num], a["Description"], a["AssignmentType"], a["DueDate"].split(" ")[0], a["Points"], a["Possible"]])

            #calc grade stuff
            #weight = re.findall("\((.*)\)", a["AssignmentType"])[0]
            #print (weight)
            key = a["AssignmentType"]
            if key not in weights.keys():
                weights[key] = [(a["Points"], a["Possible"])]
            else:
                weights[key].append((a["Points"], a["Possible"]))
        rowstoput = ""
        for i in range(len(names)):
            #Print assignment
            #names, category, date, points, possible points
            rowstoput += row.format(names[i], category[i], duedate[i], points[i], possible[i])
        catstoput = ""
        done = {}
        for i in category:
            if i in done:
                continue
            grades = weights[i]
            numerator = 0.0
            denom = 0.0
            for b in grades:
                if b[0] == "Z":
                    denom += float(b[1])
                elif b[0] == "X" or b[0] == "":
                    pass
                else:
                    numerator += float(b[0])
                    denom += float(b[1])
            
            
            if denom == 0.0:
                done[i] = ["NG", numerator, denom]
                catstoput += row2.format(i, i.split("(")[1].split(")")[0], str(numerator) + "/" + str(denom), "NG")
            else:
                done[i] = [(round(numerator / denom), 4) * 100, numerator, denom]
                catstoput += row2.format(i, i.split("(")[1].split(")")[0], str(numerator) + "/" + str(denom),  str(round(numerator / denom, 4) * 100) + "%")
        toprint = classtemplate.format(cats=catstoput, head=classname, rows=rowstoput, grade=calculate_grade(weights), id=num, classnametable=(classname.replace(" ", "") + "table"), classnamegrade=(classname.replace(" ", "") + "grade"))
        gradestoput += toprint
        rowstoput = ""
        for i in missing:
            rowstoput = row2.format(i[2], i[3], i[4], i[5])
            toprint = classtemplate2.format(head=i[1], rows=rowstoput, grade=classname, id=str(c_missing))
            missingtoput += toprint
            c_missing += 1
        
        #dynamically generate classes dropdown
        classdropdown += '<option value="{}">{}</option>'.format(classname, classname)
        counter += 1



    #creating upcoming assignments
    try:
        assigns = open(str(stu.studentnum) + ".txt", "r").read()
    except:
        assigns = open(str(stu.studentnum) + ".txt", "w")
        assigns.close()
        assigns = open(str(stu.studentnum) + ".txt", "r").read()
    c = 1
    if len(assigns) > 0:
        for i in assigns.strip().split("\n"):
            data = i.split("|||")
            temp = row3.format(data[2] + " " + buttontemp2.format(data[5], data[5]), data[3], data[4])
            ret = calc_prio(data)
            upcomingtoput += classtemplate3.format(head=data[0] + " | " + data[1], rows=temp, grade="Priority: " + str(ret[0]), id=str(c), message=ret[1])
            c += 1

        
    return flask.render_template("main.html", grub=stu.grubmsg, classesdrop=classdropdown, missingwork=missingtoput, grades=gradestoput, studentid=stu.studentnum, upcomingwork=upcomingtoput)

def create_grub(classname):
    info = 0
    for num in order:
        
        if classmap[num] == escape(classname):
            info = copy.deepcopy(dic[classmap[num]])
            break
    weights = {}
    
    for a in info:
        if len(a.keys()) == 0:
            continue

        key = a["AssignmentType"]
        if key not in weights.keys():
            weights[key] = [(a["Points"], a["Possible"])]
        else:
            weights[key].append((a["Points"], a["Possible"]))
    currentgrade = float(calculate_grade(weights).strip("%"))
    if currentgrade >= 89.5:
        return "You already have an A!"
    away = math.ceil(currentgrade/10.0)*10.0-0.5 - currentgrade

    
    bestgrade = 0.0
    bestmax = 0.0
    bestassignment = ""
    if "Formative (40)" in weights or "Summative (50)" in weights or "All Tasks/Assessments (100)" in weights:
        for a in info:
            if len(a.keys()) == 0:
                continue
            if a["AssignmentType"] == "Formative (40)" or a["AssignmentType"] == "Summative (50)" or a["AssignmentType"] == "All Tasks/Assessments (100)":
                if a["Points"] == "Z" or a["Points"] == "X" or a["Points"] == "":
                    continue
                if round(float(a["Points"])**3/float(a["Possible"])**2, 4)*100 > bestmax:
                    bestmax = round(float(a["Points"])**3/float(a["Possible"])**2, 4)*100
                    bestgrade = round(float(a["Points"])/float(a["Possible"]), 4)*100
                    bestassignment = a["Description"]
    else:
        return "You do not have enough grades to Grade Grub."
    print(bestgrade)
    print(bestassignment)
    tname = ""
    studentname = ""
    email= ""
    for i in stu.classes:
        if i["courseName"] == escape(classname):
            
            tname = " ".join(i["teacher"].split(", ")[::-1])
            studentname = " ".join(i["student"].split(", ")[::-1])
            email = i["email_addr"]
            break
    print(tname)
    
    print(studentname)
    def calcletter(n):
        if n>=89.5:
            return 'an A'
        if n>= 79.5:
            return 'a B'
        if n >= 69.5:
            return 'a C'
        if n >= 59.5:
            return 'a D'
        return 'an E'
    r = """<div id="reply">
    <div class="form-group basic-textarea">
      <label for="grubtext">Send this email to %s:</label>
      <textarea class="form-control" id="grubtext" rows="10" style="height:auto;">"""%(email)
    r += "Dear %s,\n\nI was just checking portal today and I noticed that I have a %s in your class."%(tname,currentgrade) + \
    " As you know, this grade is only %s percent away from %s. I was wondering if it would be possible for you to bump up my grade? "%(away, calcletter(math.ceil(currentgrade/10.0)*10.0))
    r += "I have been demonstrating high amounts of effort in your class, which can be seen in how I got %s on the '%s' assignment. I would really appreciate it if you could consider this.\n\n"%(calcletter(bestgrade), bestassignment)
    r += "Thanks, and have a great day!\n%s</textarea></div></div>"%(studentname)
    print(r)
    return r

    
    

def calc_prio(data):
    
    classname = data[0]
    info = 0
    for num in order:
        
        if classmap[num] == escape(classname):
            info = copy.deepcopy(dic[classmap[num]])
            break
    
    target = 89.5
    if stu.getMP1Grades()[escape(classname)] == "A":
        target = 79.5

    weights = {}
    
    for a in info:
        if len(a.keys()) == 0:
            continue

        key = a["AssignmentType"]
        if key not in weights.keys():
            weights[key] = [(a["Points"], a["Possible"])]
        else:
            weights[key].append((a["Points"], a["Possible"]))
        
    currentgrade = float(calculate_grade(weights).strip("%"))
    tankability = currentgrade - target

    #assume 100
    temp = copy.deepcopy(weights)
    category = data[2]
    possible = data[4]
    if category not in temp:
        temp[category] = [(possible, possible)]
    else:
        temp[category].append((possible, possible))
    sicegrade = float(calculate_grade(temp).strip("%"))

    #assume 0
    temp = copy.deepcopy(weights)
    if category not in temp:
        temp[category] = [("0", possible)]
    else:
        temp[category].append(("0", possible))
    ripgrade = float(calculate_grade(temp).strip("%"))

    gradechange = sicegrade - ripgrade

    duedate = data[3]
    date1 = dateparser.parse(duedate).date()
    date2 = datetime.date.today()

    daysaway = date1 - date2
    numerator = max(gradechange-tankability, 0)
    prio = round((numerator)**2*1.0/(daysaway.days + 1), 2)
    

    text1 = "If you got 100% on this assignment, you would have a {}% in the class.".format(str(round(sicegrade, 2)))
    text2 = "If you got a 0% on this assignment, you would have a {}% in the class.".format(str(round(ripgrade, 2)))
    col = 'muted'
    if gradechange <= 5:
        col = 'success'
    elif gradechange <= 15:
        col = 'warning'
    else:
        col = 'danger'
    text3 = "This is a <span class=\"text-{}\">{}%</span> difference.".format(col, str(round(gradechange, 2)))
    
    s = 'in '+str(daysaway.days)+' days.'
    col = 'success'
    if daysaway.days == 0:
        s = 'today!'
        col = 'danger'
    if daysaway.days == 1:
        s = 'tomorrow.'
        col = 'warning'
        
    text4 = "This assignment is due <span class=\"text-{}\">{}</span>".format(col, s)

    sol = 0
    for cur in range(0,int(float(data[4]))*2,1):
        sol = cur / 2.0
        temp = copy.deepcopy(weights)
        if category not in temp:
            temp[category] = [(str(sol), possible)]
        else:
            temp[category].append((str(sol), possible))
        kekgrade = float(calculate_grade(temp).strip("%"))
        if kekgrade >= currentgrade//10*10-0.5:
            break
    col = 'muted'
    if kekgrade <= 50:
        col = 'success'
    elif kekgrade <= 90:
        col = 'warning'
    else:
        col = 'danger'
    text5 = "You need a <span class=\"text-{}\">{}/{}</span> on this assignment to maintain your current grade.".format(col,str(sol), str(possible))

    if currentgrade < 89.5 and sicegrade > 89.5:
        sol = 0
        for cur in range(0,int(float(data[4]))*2,1):
            sol = cur / 2.0
            temp = copy.deepcopy(weights)
            if category not in temp:
                temp[category] = [(str(sol), possible)]
            else:
                temp[category].append((str(sol), possible))
            kekgrade = float(calculate_grade(temp).strip("%"))
            if kekgrade >= 89.5:
                break
        col = 'muted'
        if kekgrade <= 50:
            col = 'success'
        elif kekgrade <= 90:
            col = 'warning'
        else:
            col = 'danger'
        text5 += '<br>You need a <span class=\"text-{}\">{}/{}</span> on this assignment to get an A in the class.'.format(col,str(sol), str(possible))
    col = 'muted'
    lqg = stu.getMP1Grades()[escape(classname)]
    if lqg == 'A':
        col = 'success'
    elif lqg == 'B':
        col = 'warning'
    else:
        col = 'danger'
    text6 = "You got an <span class=\"text-{}\">{}</span> in this class last quarter.".format(col,lqg)
    
    ret = [prio, "<p>" + text1 + "<br>" + text2 + "<br>" + text3 + "<br><br>" + text4 + "<br><br>" + text5 + "<br><br>" + text6 + "</p>"]
    return ret

    

def calculate_grade(weights):
    #print(weights)
    final_grade = 0.0
    total_weight = 0.0
    for a in weights.keys():
        weight = float(re.findall("\((.*)\)", a)[0])
        numerator = 0.0
        denominator = 0.0
        for b in weights[a]:
            if b[0] == "" or b[0] == "X":
                continue
            elif b[0] == "Z":
                denominator += float(b[1])
            else:
                numerator += float(b[0])
                denominator += float(b[1])
        if denominator != 0:
            final_grade += (numerator * 100.0 / denominator) * (weight / 100.0)
            total_weight += weight
    if total_weight == 0:
        return "0.0%"
    #print(str(final_grade / (total_weight / 100)))
    return str(round(final_grade / (total_weight / 100.0), 2)) + "%"

@app.route('/class', methods=['POST'])
def post_handler():
    data = (flask.request.form)

    if "removeupcoming" in data:
        toremove = data["id"]
        fi = open(str(stu.studentnum) + ".txt", "r").read().split("\n")
        for a in range(len(fi)):
            if fi[a].endswith(toremove):
                del fi[a]
                break
        fo = open(str(stu.studentnum) + ".txt", "w")
        fo.write("\n".join(fi))
        fo.close()

    if "removegrade" in data:
        toremove = data["id"]
        for i in range(len(stu.hypclasses)):
            if stu.hypclasses[i][1]["hyp"] == toremove:
                del stu.hypclasses[i]
                break
        
    
    if "classname" in data:
    #ImmutableMultiDict([('title', 'title'), ('classname', 'AP CHEMSTRY DP A'), ('category', 'Homework (10)'), ('date', '2017-12-02'), ('points', '69points')])
    
        towrite = "{}|||{}|||{}|||{}|||{}|||{}".format(data["classname"], data["title"], data["category"], data["date"], data["points"], "grades" + str(stu.upcount))
        stu.upcount += 1
        fo = open(str(stu.studentnum) + ".txt", "a")
        fo.write(towrite + "\n")
        fo.close()
        fo = open(str(stu.studentnum) + ".txt", "r")
    elif "classname2" in data:
        #ImmutableMultiDict([('category2', 'Summative (50)'), ('points2', '5'), ('possible2', '6'), ('date2', '2017-12-02'), ('title2', 'Test Assignment'), ('classname2', 'AP CHEMSTRY DP A')])
        
        info = {"hyp" : ("remove" + str(len(stu.hypclasses))), "Description":data["title2"], "AssignmentType":data["category2"], "DueDate":(str(data["date2"])+" 00:00:00.0"), "Points":str(float(data["points2"])), "Possible":data["possible2"]}
        stu.hypclasses.append((data["classname2"], info))
        
        #print(data)
    elif "classnamememe" in data:
        stu.grubmsg = create_grub(data['classnamememe'])
        print("SDFDSFDSF")
        print(stu.grubmsg)
    return classes()

if __name__ == '__main__':
    app.run()
