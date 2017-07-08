// Empty JS for your own code to be here
"use strict";
// window.onload = function () { alert("It's loaded!") };
document.getElementById("submit_button").onclick = function() {
  // Defining the variable
  var id_karyawan = ""
  var usr_password = ""
  // Get the value from form input
  id_karyawan = document.getElementById('id_karyawan').value;
  usr_password = document.getElementById('usr_password').value;
  //Used for logging to check whether the value succesfully pulled from the form input
  console.log(id_karyawan);
  console.log(usr_password);
  //Asynchronous HTTP request to the API server
  var xmlHttp = new XMLHttpRequest();
  var url = "http://localhost:18080/kehadiran"
  var query = "?" + "idakun=" + id_karyawan + "&" +
              "tgl_lahir=" + tgl_lahir + "&" +
              "tahun=" + tahun + "&" +
              "bulan=" + bulan + "&" +
              "usr_pass=" + usr_password;
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          callback(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url + query, true); // true for asynchronous
  xmlHttp.send(null);
  //Callback function when the asynchronous request succeeed
  var callback = function(responseText) {
    var responseText = JSON.parse(responseText);
    console.log(responseText);
    //Render the response text into the HTML table
    var tablebody = document.getElementById("tablebody");
    responseText.data.forEach(function(array){
      console.log(array[1]);
      var row = tablebody.insertRow();
      var tanggal = row.insertCell();
      tanggal.innerHTML = array[1];
      var nama = row.insertCell();
      nama.innerHTML = array[3];
      var divisi = row.insertCell();
      divisi.innerHTML = array[5];
      var masuk = row.insertCell();
      masuk.innerHTML = array[6];
      var pulang = row.insertCell();
      pulang.innerHTML = array[7];
    });
    //Show the status and message through alert
    var alertMessage = "Status: " + responseText.status + "\n" +
                    "Pesan: " + responseText.message;
    alert(alertMessage);
  };
};
