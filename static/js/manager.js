Vue.options.delimiters=["[[","]]"];
Vue.component('inventory-product',{
    props:['product'],
    template: `
    <div class="card text-dark p-1 bg-success-subtle" style="max-width: 18rem;">
        <img :src="product.img_path" class="card-img-top img-thumbnail mb-2" alt="Image">
        <div class="card-header border rounded-pill bg-success-subtle">
          <h3 class="card-title">[[product.product_name]] (P[[product.product_id]])</h3>
        </div>
        <div class="card-body">
          <p class="card-text" style="display: flex; justify-content: space-between;"><span><strong>Price : </strong><i class="bi bi-currency-rupee"></i>[[product.price]]</span><span><strong>Unit : </strong>[[product.unit]]</span><span><strong>Stock : </strong>[[product.stock]]</span></p>
          <p class="card-text" style="display: flex; justify-content: space-around;"><span><strong>Mfd : </strong>[[product.mfd.slice(0,10)]]</span><span><strong>Expd : </strong>[[product.expd.slice(0,10)]]</span></p>
          <button class="btn btn-dark" data-bs-toggle="modal" data-bs-target="#ProductPutModal" @click="productFetcher(product)"> <i class="bi bi-pencil-square" style="font-size: 1.5rem;"></i> </button>
        </div>
        <div v-show="product.stock < 1" class="card-footer alert alert-success-subtle rounded"><strong>Stockout</strong></div>
    </div>`,
    methods: {
      productFetcher(i){
        this.$emit('modding',i)

        }
    },
    created(){
        // console.log('hi');
      this.product.img_path = 'static/images/products/'+this.product.product_id + '.png'
    }
}) 


new Vue({
    el: '#app',
    data: {
      sections: [],
      secX: {
        id: null,
        name: null,
      },
      prodX: {
        id: null,
        name: null,
        section: null,
        price: null,
        stock: null,
        unit: null,
        mfd: null,
        expd: null
      },
      passkey: null
    },
    methods: {
      dataFetcher() {
        fetch('http://127.0.0.1:8080/api/section/all')
        .then(response => response.json())
        .then(data => {
          data.forEach(obj => {
            obj.showProducts = false;
            obj.img_path = 'static/images/sections/' + obj.category_id + '.png';
          });
          this.sections = data;
          console.log(this.sections)
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        })
      },
      sectionFetcher(i) {
        this.secX.id = i.category_id;
        this.secX.name = i.category_name;
        // alert(this.secX.id);
        this.approve()
      },
      sectionModder() {
        fetch(`http://127.0.0.1:8080/permit/${this.passkey}`)
        .then(response => response.json())
        .then(data => {
          if (data.data == "GRANTED" && this.secX.id != null && this.secX.name != null){
            fetch(`http://127.0.0.1:8080/api/section/${this.secX.id}`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ "category_name": this.secX.name })
            })
            .then(response => response.json())
            .then(data => {
              alert(data);
              this.dataFetcher();
            })
            .catch(error => {
              console.error('Error fetching data:', error);
            })
          }
          else {
            alert("Invalid Permit or Operation");
          }
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        })
      },
      sectionAdder() {
        fetch(`http://127.0.0.1:8080/permit/${this.passkey}`)
        .then(response => response.json())
        .then(data => {
          if (data.data == "GRANTED" && this.secX.name != null){
            fetch('http://127.0.0.1:8080/api/section/new', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ "category_name": this.secX.name })
            })
            .then(response => response.json())
            .then(data => {
              alert(data);
              this.dataFetcher();
            })
            .catch(error => {
              console.error('Error fetching data:', error);
            })
          }
          else {
            alert("Invalid Permit or Operation");
          }
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        })
      },
      sectionDeleter(){
        fetch(`http://127.0.0.1:8080/permit/${this.passkey}`)
        .then(response => response.json())
        .then(data => {
          if (data.data == "GRANTED"){
            fetch(`http://127.0.0.1:8080/api/section/${this.secX.id}`, {
              method: 'DELETE',
              headers: {
                'Content-Type': 'application/json'
              },
            })
            .then(response => response.json())
            .then(data => {
              alert(data);
              this.dataFetcher();
            })
            .catch(error => {
              console.error('Error fetching data:', error);
            })

            // fetch(`http://127.0.0.1:8080/delete/section/${this.secX.id}`)
            // .then(response => response.json())
            // .then(data => {
            //   alert(data)
            // })
            // .catch(error => {
            //   console.error('Error fetching data:', error);
            // })
          }
          else {
            alert("Invalid Permit or Operation");
          }
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        })
      },
      productFetcher(i) {
        
        this.approve()
        this.prodX.id = i.product_id;
        this.prodX.name = i.product_name,
        this.prodX.section = i.category_id,
        this.prodX.price = i.price,
        this.prodX.stock = i.stock,
        this.prodX.unit = i.unit,
        this.prodX.mfd = i.mfd,
        this.prodX.expd = i.expd
      },
      productModder() {
        fetch(`http://127.0.0.1:8080/permit/${this.passkey}`)
        .then(response => response.json())
        .then(data => {
          if (data.data == "GRANTED" && this.prodX.id != null){
            // alert(this.prodX.section)
            // alert(this.prodX.mfd)
            // alert(this.prodX.expd)
            fetch(`http://127.0.0.1:8080/api/product/${this.prodX.id}`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                "product_name": this.prodX.name,
                "category_id": this.prodX.section,
                "stock": this.prodX.stock,
                "unit": this.prodX.unit,
                "price": this.prodX.price,
                "mfd": this.prodX.mfd,
                "expd": this.prodX.expd
              })
            })
            .then(response => response.json())
            .then(data => {
              alert(data);
              // alert("wtf")
              this.dataFetcher();
            })
            .catch(error => {
              console.error('Error fetching data:', error);
            })
            // alert('wtf')
          }
          else {
            alert("Invalid Permit or Operation");
          }
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        })
      },
      productAdder() {
        fetch(`http://127.0.0.1:8080/permit/${this.passkey}`)
        .then(response => response.json())
        .then(data => {
          if (data.data == "GRANTED" && this.prodX.name != null && this.prodX.section != null && this.prodX.unit != null && this.prodX.stock != null && this.prodX.price != null && this.prodX.mfd != null && this.prodX.expd != null){
            fetch('http://127.0.0.1:8080/api/product/new', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                "product_name": this.prodX.name,
                "category_id": this.prodX.section,
                "stock": this.prodX.stock,
                "unit": this.prodX.unit,
                "price": this.prodX.price,
                "mfd": this.prodX.mfd,
                "expd": this.prodX.expd
              })
            })
            .then(response => response.json())
            .then(data => {
              alert(data);
              this.dataFetcher();
            })
            .catch(error => {
              console.error('Error fetching data:', error);
            })
          }
          else {
            alert("Invalid Permit or Operation");
          }
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        })
      },
      productDeleter(){
        fetch(`http://127.0.0.1:8080/permit/${this.passkey}`)
        .then(response => response.json())
        .then(data => {
          if (data.data == "GRANTED"){
            fetch(`http://127.0.0.1:8080/api/product/${this.prodX.id}`, {
              method: 'DELETE',
              headers: {
                'Content-Type': 'application/json'
              },
            })
            .then(response => response.json())
            .then(data => {
              alert(data);
              this.dataFetcher();
            })
            .catch(error => {
              console.error('Error fetching data:', error);
            })
          }
          else {
            alert("Invalid Permit or Operation");
          }
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        })
      },
      toggleStyle(section) {
      section.showProducts = !section.showProducts;
      },
      approve(){
        fetch('http://127.0.0.1:8080/OTP')
        alert('Awaiting Approval...')
      }
    },
    created(){
      this.dataFetcher();
      
    }
  });



