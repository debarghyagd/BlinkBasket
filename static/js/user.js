Vue.options.delimiters = ['[[',']]'];


var app = new Vue({
    el: "#app",
    data: {
        user: {},
    },
    created(){
        fetch('http://127.0.0.1:8080/get-users/this')
        .then(response => response.json())
        .then(data => {
            this.user = data;
            this.user.isStaff = (this.user.roles.includes('Admin') || this.user.roles.includes('Manager'))
        })
        .catch(error => {
            console.error('Error fetching data:', error);
          });
    }
})