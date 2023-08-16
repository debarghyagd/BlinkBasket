Vue.options.delimiters = ['[[',']]'];


var app = new Vue({
    el: "#app",
    data: {
        info: {
            'summary' :{
              'nUsers': null,
              'nOrders': null,
              'tRevenue': null,
              'nSections': null,
              'nProducts': null,
              'tStock': null,
              'month': null,
            }},
        isExportReady: null
    },
    methods: {
        exportJob() {
            alert('Starting export job...')
            fetch('http://127.0.0.1:8080/async')
            .then(response => response.json())
            .then(data => {
                alert(data.resp)
                this.isExportReady = !this.isExportReady
                alert('Click again to download')
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
        },
    },
    created(){
        fetch('http://127.0.0.1:8080/summary/data')
        .then(response => response.json())
        .then(data => {
            this.info = data;
            this.info.pie_path = 'static/images/charts/Pie_0.png'
            this.info.bar_rev_path = 'static/images/charts/Bar_0R.png'
            this.info.bar_sto_path = 'static/images/charts/Bar_0S.png'
            this.info.line_path = 'static/images/charts/Line_0.png'
            this.isExportReady = false
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    }
})