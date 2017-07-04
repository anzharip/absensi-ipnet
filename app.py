# Import builtin module
import json
from bottle import Bottle, run, request, response
import mysql.connector
import datetime
import time
import os
import sys
# Import custom module
import parsercsv
import config
import sqlstatement

DBHOST = config.DBHOST
DBNAME = config.DBNAME
DBUSER = config.DBUSER
DBPASS = config.DBPASS
APIHOST = config.APIHOST
APIPORT = config.APIPORT

getcompletedata = parsercsv.getcompletedata
tosqlrecord = parsercsv.tosqlrecord
uploaddivisi = parsercsv.uploaddivisi
uploadkaryawan = parsercsv.uploadkaryawan
uploadkehadiran = parsercsv.uploadkehadiran

sql_query = sqlstatement.sql_query

class InputData(object):
    def __init__(self, data, maxlen=255):
        self.data = data
        self.isalnum = data.isalnum()
        self.isdigit = data.isdigit()
        self.isspace = data.isspace()
        self.len = len(data)
        self.maxlen = maxlen
    def islenvalid(self):
        if self.len < 1:
            return False
        elif self.len > self.maxlen:
            return False
        else:
            return True
    def istypevalid(self):
        return True
    def isvalid(self):
        return self.istypevalid() and self.islenvalid()

class IDAkun(InputData):
    def istypevalid(self):
        return self.isdigit
    def inputtype(self):
        return "idakun"

class Password(InputData):
    def inputtype(self):
        return "password"

class Tanggal(InputData):
    def istypevalid(self):
        return self.isdigit
    def islenvalid(self):
        if self.len is not 8:
            return False
        else:
            return True
    def inputtype(self):
        return "tanggal"

class Tahun(InputData):
    def istypevalid(self):
        if self.isdigit:
            if 1900 <= int(self.data) <= time.strftime("%Y"):
                return True
            else:
                return False
        else:
            return False
    def islenvalid(self):
        if self.len is not 4:
            return False
        else:
            return True
    def inputtype(self):
        return "tahun"

class Bulan(InputData):
    def istypevalid(self):
        if self.isdigit:
            if 1 <= int(self.data) <= 12:
                return True
            else:
                return False
        else:
            return False
    def inputtype(self):
        return "bulan"

def validateinput(inputdata):
    if inputdata.isvalid() is False:
        json_res = {
          "status": "error",
          "message": "Tipe input %s: terdapat karakter ilegal atau panjang variable tidak sesuai (panjang 1 - %s karakter). " % (inputdata.inputtype(), inputdata.maxlen),
          "data": ""
        }
        return False, json.dumps(json_res)
    else:
        return True, None

app = Bottle()

# Required to handle CORS mechanism in browser
@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

@app.post('/akun/create')
def post_akun_create():
    import hashlib
    response.content_type = "application/json"
    enc_pass = hashlib.sha512()
    upload = request.files.get('upload') or ''
    idakun = IDAkun(request.forms.get('idakun'), 6)
    usr_pass = Password(request.forms.get('pass'), 255)
    if validateinput(idakun)[0] is False:
        return validateinput(idakun)[1]
    if validateinput(usr_pass)[0] is False:
        return validateinput(usr_pass)[1]
    enc_pass.update(usr_pass.data)
    try:
        dataakun = sql_query('''SELECT * FROM %s.karyawan \
            WHERE id = %s AND id_divisi_fk = 100001 AND enc_pass = "%s";''' % (DBNAME, idakun.data, enc_pass.hexdigest()))
    except mysql.connector.Error:
        json_res = {
            "status": "error",
            "message": "Kesalahan sistem: tidak bisa menghubungi basis data",
            "data": "",
        }
        return json.dumps(json_res)
    except:
        raise
    if len(dataakun) is 0:
        json_res = {
            "status": "error",
            "message": "ID/password tidak ditemukan",
            "data": "",
        }
        return json.dumps(json_res)
    try:
        name, ext = os.path.splitext(upload.filename)
    except:
        json_res = {
            "status": "error",
            "message": "Berkas gagal diunggah. Mohon pilih berkas dengan benar dan coba kembali. ",
            "data": "",
        }
        return json.dumps(json_res)
    if ext not in ('.csv'):
        json_res = {
            "status": "error",
            "message": "Ekstensi file harus .CSV",
            "data": "",
        }
        return json.dumps(json_res)
    try:
        f = upload.file
        completedata = getcompletedata(f)
        sqlrecord = tosqlrecord(completedata)
        print "Uploading to divisi table..."
        uploaddivisi(completedata)
        print "Uploading to karyawan table..."
        uploadkaryawan(completedata)
        print "Uploading to kehadiran table..."
        uploadkehadiran(sqlrecord)
    except:
        e = sys.exc_info()[0]
        print e
        json_res = {
            "status": "error",
            "message": "Upload data karyawan dan kehadiran gagal. Hubungi administrator. ",
            "data": "",
        }

        return json.dumps(json_res)
    json_res = {
        "status": "ok",
        "message": "Upload data karyawan dan kehadiran berhasil",
        "data": "",
    }
    return json.dumps(json_res)

@app.get('/kehadiran')
def get_kehadiran():
    import hashlib
    idakun = IDAkun(str(request.query.idakun), 6)
    if validateinput(idakun)[0] is False:
        return validateinput(idakun)[1]
    tgl_lahir = Tanggal(str(request.query.tgl_lahir), 8)
    if validateinput(tgl_lahir)[0] is False:
        return validateinput(tgl_lahir)[1]
    tahun = Tahun(str(request.query.tahun), 4)
    if validateinput(tahun)[0] is False:
        return validateinput(tahun)[1]
    bulan = Bulan(str(request.query.bulan), 2)
    if validateinput(bulan)[0] is False:
        return validateinput(bulan)[1]
    usr_pass = Password(str(request.query.usr_pass))
    if validateinput(usr_pass)[0] is False:
        return validateinput(usr_pass)[1]
    enc_pass = hashlib.sha512()
    enc_pass.update(usr_pass.data)
    response.content_type = "application/json"
    def datetime_handler(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, 'resolution'):
            hours, remainder = divmod(obj.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return "%s:%s:%s" % (hours, minutes, seconds)
        else:
            raise
    try:
        dataakun = sql_query('''SELECT * FROM %s.karyawan \
            WHERE id = %s AND enc_pass = "%s";''' % (DBNAME, idakun.data, enc_pass.hexdigest()))
    except mysql.connector.Error:
        json_res = {
            "status": "error",
            "message": "Kesalahan sistem: tidak bisa menghubungi basis data",
            "data": "",
        }
        return json.dumps(json_res)
    except:
        raise
    if len(dataakun) is 0:
        json_res = {
            "status": "error",
            "message": "ID/password tidak ditemukan",
            "data": "",
        }
        return json.dumps(json_res)
    try:
        data = sql_query('''SELECT t1.id, t1.tanggal, t1.id_karyawan_fk, t2.nama, t2.id_divisi_fk, t3.nama_div, t1.masuk, t1.pulang \
            FROM %s.kehadiran t1 JOIN %s.karyawan t2 JOIN %s.divisi t3 ON t1.id_karyawan_fk = t2.id AND t2.id_divisi_fk = t3.id \
            WHERE t2.id = %s AND t2.enc_pass = '%s' AND tgl_lahir = DATE("%s") AND YEAR(tanggal) = %s AND MONTH(tanggal) = %s \
            ORDER BY t1.id ASC;''' % (DBNAME, DBNAME, DBNAME, idakun.data, enc_pass.hexdigest(), tgl_lahir.data, tahun.data, bulan.data))
    except mysql.connector.Error:
        json_res = {
            "status": "error",
            "message": "Kesalahan sistem: tidak bisa menghubungi basis data",
            "data": "",
        }
        return json.dumps(json_res)
    except:
        raise
    json_res = {
        "status": "ok",
        "message": "Data berhasil diambil",
        "data": data
    }
    return json.dumps(json_res, default=datetime_handler)

run(app, host=APIHOST, port=APIPORT)
