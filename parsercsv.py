# Import custom module
import config
import sqlstatement
import re

DBHOST = config.DBHOST
DBNAME = config.DBNAME
DBUSER = config.DBUSER
DBPASS = config.DBPASS

sql_query = sqlstatement.sql_query
sql_insert = sqlstatement.sql_insert

# Open file with name and readonly mode
def getdataaslist(fileobj):
    list = []
    for line in fileobj:
        list.append(line)
    return list

def getendpos(datalist):
    listreturn = []
    attendancelinestart = 9
    linepos = 0
    for line in datalist:
        if ";" in line[:1]:
            if linepos >= attendancelinestart:
                listreturn.append(linepos)
        linepos = linepos + 1
    listreturn.append(len(datalist))
    return listreturn

def isnoisedata(startpos, endpos, datalist):
    checknoisedata = range(startpos, endpos)
    concatenateddata = ""
    for line in checknoisedata:
        concatenateddata = concatenateddata + str(datalist[line])
    if "Nama" in concatenateddata:
        return True
    else:
        return False

def getstartendpos(endposlist, datalist):
    listreturn = []
    linepos = 0
    for line in endposlist:
        if linepos < (len(endposlist) - 1):
            if isnoisedata((endposlist[linepos] + 1), endposlist[linepos + 1], datalist) is False:
                listreturn.append([(endposlist[linepos] + 1), endposlist[linepos + 1]])
            linepos = linepos + 1
    return listreturn

def getpersondata(datalist, startendpos, posnum):
    linepos = startendpos[posnum][0]
    output = []
    while linepos <= (startendpos[posnum][1] - 1):
        output.append(datalist[linepos])
        linepos = linepos + 1
    return output

def getpersonname(lists):
    output = ""
    for line in lists:
        if ((line[:1].isalpha()) or ("\"" in line[:1])):
            if "Nama" not in line:
                output = output + line + " "
    output = output.replace("\n", "")
    output = output.replace("\"", "")
    return output[:(output.find("("))].strip()

def getpersonid(lists):
    output = ""
    for line in lists:
        if ("(" in line) or (")" in line):
            output = output + line
    output = output.replace("\n", "")
    output = output.replace("\"", "")
    return output[(output.find("(") + 1):(output.find(")"))]

def getdivname(dataaslist):
    divpos = 8
    divnum = dataaslist[divpos][:dataaslist[divpos].find(".")]
    divname = dataaslist[divpos][(dataaslist[divpos].find(".") + 1):dataaslist[divpos].find(";")]
    divnum = divnum.strip()
    divname = divname.strip()
    return [divnum, divname]

def getyear(dataaslist):
    yearpos = 1
    yearline = dataaslist[yearpos]
    yearline = yearline.replace(";", "")
    yearline = yearline.replace("Dari", "")
    yearline = yearline.strip()
    year = yearline[6:10]
    return year

def getstartenddate(dataaslist):
    year = getyear(dataaslist)
    datepos = 6
    dateline = dataaslist[datepos].strip()
    emptycol = [34, 25, 12, 1, 0]
    dateline = dateline.replace("\"", "")
    dateline = dateline.replace("\n, ", "")
    startenddate = dateline.split(";")
    for line in emptycol:
        del startenddate[line]
    beautified = []
    for line in startenddate:
        if re.search('[a-zA-Z]', line):
            print 'line', line
            print 'line[3:6]', line[3:6]
            date = ''
            if str(line[3:6]) is 'Jan':
                beautified.append(year + "-" + line[0:2] + "-" + '01')
            elif str(line[3:6]) is 'Feb':
                beautified.append(year + "-" + line[0:2] + "-" + '02')
            elif str(line[3:6]) is 'Mar':
                beautified.append(year + "-" + line[0:2] + "-" + '03')
            elif str(line[3:6]) is 'Apr':
                beautified.append(year + "-" + line[0:2] + "-" + '04')
            elif str(line[3:6]) is 'Mei':
                beautified.append(year + "-" + line[0:2] + "-" + '05')
            elif str(line[3:6]) is 'Jun':
                beautified.append(year + "-" + line[0:2] + "-" + '06')
            elif str(line[3:6]) is 'Jul':
                beautified.append(year + "-" + line[0:2] + "-" + '07')
            elif str(line[3:6]) is 'Agu':
                beautified.append(year + "-" + line[0:2] + "-" + '08')
            elif str(line[3:6]) is 'Sep':
                beautified.append(year + "-" + line[0:2] + "-" + '09')
            elif str(line[3:6]) is 'Okt':
                beautified.append(year + "-" + line[0:2] + "-" + '10')
            elif str(line[3:6]) is 'Nov':
                beautified.append(year + "-" + line[0:2] + "-" + '11')
            elif str(line[3:6]) is 'Des':
                beautified.append(year + "-" + line[0:2] + "-" + '12')
        else:
            beautified.append(year + "-" + line[3:5] + "-" + line[0:2])
    return beautified

def getattendance(dataaslist, startendline):
    concat = ''
    for line in dataaslist[startendline[0]:startendline[1]]:
        concat = concat + line
    concat = concat.replace("\"", "")
    concat = concat.replace("\n", "")
    csv = concat.split(";")
    emptycol = [34, 25, 12, 1, 0]
    csvstrip = []
    for line in csv:
        csvstrip.append(line.strip())
    for line in emptycol:
        del csvstrip[line]
    beautified = []
    for line in csvstrip:
        if line == "":
            beautified.append("-".split("-"))
        else:
            beautified.append(line.split("-"))
    beautifiest = []
    for line in beautified:
        if len(line) is 1:
            beautifiest.append([line[0], ""])
        else:
            beautifiest.append(line)
    return beautifiest

def getcompletedata(fileobj):
    dataaslist = getdataaslist(fileobj)
    dataendpos = getendpos(dataaslist)
    datastartendpos = getstartendpos(dataendpos, dataaslist)
    counter = 0
    completedata = []
    for line in datastartendpos:
        persondata = getpersondata(dataaslist, datastartendpos, counter)
        completedata.append([getpersonname(persondata), getpersonid(persondata), getdivname(dataaslist), getstartenddate(dataaslist), getattendance(dataaslist, line)])
        counter = counter + 1
    return completedata

def tosqlrecord(completedata):
    sqlrecord = []
    for person in completedata:
        datelist = person[3]
        counter = 0
        for data in datelist:
            name = person[0]
            nameid = person[1]
            divid = person[2][0]
            divname = person[2][1]
            date = data
            attendin = person[4][counter][0]
            attendout = person[4][counter][1]
            counter = counter + 1
            record = [date, name, nameid, divid, divname, attendin, attendout]
            sqlrecord.append(record)
    return sqlrecord

def isidexist(idnum, table):
    query = sql_query("select * from %s where %s.id=%s;" % (table, table, idnum))
    if not query:
        return False
    else:
        return True

def uploaddivisi(completedata):
    sqltablename = "divisi"
    sqlidnum = completedata[0][2][0]
    sqldivname = completedata[0][2][1]
    if isidexist(sqlidnum, sqltablename) is True:
        print "ID exist: %s, %s" % (sqlidnum, sqldivname)
    else:
        print "Uploading: %s, %s" % (sqlidnum, sqldivname)
        sql_insert("INSERT INTO %s.%s (`id`, `nama_div`) VALUES ('%s', '%s');" % (DBNAME, sqltablename, sqlidnum, sqldivname))

def uploadkaryawan(completedata):
    import random
    import hashlib
    sqltablename = "karyawan"
    for karyawan in completedata:
        enc_pass = hashlib.sha512()
        enc_pass.update("password")
        sqlidnum = karyawan[1]
        sqlkaryawanname = karyawan[0]
        sqldivname = karyawan[2][0]
        re.escape(enc_pass)
        re.escape(sqlidnum)
        re.escape(sqlkaryawanname)
        re.escape(sqldivname)
        birthdate =  "%s-%s-%s" % (random.randint(1950, 1990), random.randint(1, 12), random.randint(1, 28))
        if isidexist(sqlidnum, sqltablename) is True:
            print "ID exist: %s, %s, %s, %s" % (sqlidnum, sqlkaryawanname, sqldivname, birthdate)
        else:
            print "Uploading: %s, %s, %s, %s" % (sqlidnum, sqlkaryawanname, sqldivname, birthdate)
            sql_insert("INSERT INTO %s.%s (`id`, `nama`, `id_divisi_fk`, `tgl_lahir`, `enc_pass`) VALUES ('%s', '%s', '%s', '%s', '%s');" % \
                       (DBNAME, sqltablename, sqlidnum, sqlkaryawanname, sqldivname, birthdate, enc_pass.hexdigest()))

def iskehadiranexist(sqlidkaryawan, sqltanggal):
    query = sql_query("SELECT * FROM %s.kehadiran WHERE kehadiran.tanggal = DATE(%s) AND kehadiran.id_karyawan_fk = %s;" % \
                      (DBNAME, sqltanggal, sqlidkaryawan))
    if not query:
        return False
    else:
        return True

def uploadkehadiran(sqlrecord):
    sqltablename = "kehadiran"
    for kehadiran in sqlrecord:
        sqltanggal = kehadiran[0].replace("-", "")
        sqlid_karyawan_fk = kehadiran[2]
        sqlmasuk = kehadiran[5]
        sqlpulang = kehadiran[6]
        if iskehadiranexist(sqlid_karyawan_fk, sqltanggal):
            print "Kehadiran exist: '%s', '%s', '%s', '%s'" % (sqltanggal, sqlid_karyawan_fk, sqlmasuk, sqlpulang)
        else:
            print "Uploading: '%s', '%s', '%s', '%s'" % (sqltanggal, sqlid_karyawan_fk, sqlmasuk, sqlpulang)
            sql_insert("INSERT INTO %s.%s (`tanggal`, `id_karyawan_fk`, `masuk`, `pulang`) VALUES ('%s', '%s', '%s', '%s');" % \
                       (DBNAME, sqltablename, sqltanggal, sqlid_karyawan_fk, sqlmasuk, sqlpulang))
