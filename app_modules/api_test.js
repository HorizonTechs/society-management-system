// add user
function add_user(){
    fetch("/signup", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "email": "Admin@email.com",
            "name": "Admin",
            "phone": "999999",
            "password": "Password2#",
            "icode": "397249"
        })
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

//login
function login(){


    let url = '/login';
    let username = 'Admin@email.com';
    let password = 'Password2#';

    let headers = new Headers();

    headers.set('Authorization', 'Basic ' + btoa(username + ":" + password));

    fetch(url, {method:'GET',
            headers: headers
        })
    .then(response => response.text())
    .then(json => console.log(json))
    .catch(error=> console.log(error))
}

// Test Society
function get_societies(){
    fetch("/societies",{
        headers: {"Authorization": "Bearer: " + token}
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function add_societies(){
    fetch("/addSociety", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"pin_code": 700136, "name": "New Society", "address": "Majhipara, Dashadrone"})
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function update_society(){
    fetch("/updateSociety", {
        method: 'PUT',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"id": 3, "pin_code": 700140, "name": "New Society", "address": "Majhipara, Dashadrone"})
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function delete_society(id){
    fetch("/deleteSociety/" + id, {
        method: 'DELETE',
        headers: {"Content-Type": "application/json"}
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

// Test Member
function get_society_flats(){
    fetch("/getSocietyMembers?id=1")
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function add_flat(){
    fetch("/addFlat", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "flat_code": "2A",
            "area": 994,
            "society_id": "1",
            "balance": 0,
            "owner_id": 1
        })
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

// Test Collection

function get_collection_types(){
    fetch("/collection-types")
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function add_collection_type(){
    fetch("/addCollectionType", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "type": "Monthly"})
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function update_collection_type(){
    fetch("/updateCollectionType", {
        method: 'PUT',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"id":1, "type":"Quaterly"})
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function delete_collection_type(){
    fetch("/deleteCollectionType/1", {
        method: 'DELETE',
        headers: {"Content-Type": "application/json"}
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function get_collections(){
    fetch("/collections")
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

function add_collection(){
    let dt = new Date()
    let date = `${dt.getFullYear()}-${dt.getMonth()}-${dt.getDate()}`
    fetch("/addCollection", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "type_id": 1,
            "rate": "2/sqft",
            "society_id": 1,
            "collection_start_date": date})
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

// Transaction test

function add_payment_method(){
    fetch("/addPaymentMethod", {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"method": "GPay"})
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.log(error))
}

// Collection

function addCollection(){
    fetch("https://hd-society-management-system.herokuapp.com/addCollection", {
        method: "POST",
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify({
            "name": "Collection for Feb",
            "typeId": 1,
            "rate": 2,
            "fixed": false,
            "societyId": 1,
            "collectionStartDate": "2022-02-12"
        })
    })
    .then(response => response.text())
    .then(data=> console.log(data))
    .catch(error => console.log(error))
}