Vue.options.delimiters=["[[","]]"];
Vue.component('shop-product',{
  props:['product'],
  template: `
  <div class="card text-dark p-1 bg-success-subtle" style="max-width: 18rem;">
    <img :src="product.img_path" class="card-img-top img-thumbnail mb-2" alt="Image">
    <div class="card-header border rounded-pill bg-success-subtle">
      <h3 class="card-title">[[product.product_name]]</h3>
    </div>
    <div class="card-body">
      <p class="card-text" style="display: flex; justify-content: space-between;"><span><strong>Price : </strong><i class="bi bi-currency-rupee"></i> [[product.price]]</span><span><strong>Unit : </strong>[[product.unit]]</span></p>
      <button class="btn btn-success" v-if="!product.isCarted" @click="addCart(product)"> <i class="bi bi-cart-plus" style="font-size: 1.5rem;"></i> </button>
      <button class="btn btn-success" v-if="product.isCarted" @click="addCart(product)"disabled> <i class="bi bi-cart-plus" style="font-size: 1.5rem;"></i> </button>
    </div>
    <div v-show="product.stock <= 0" class="card-footer alert alert-danger-subtle rounded"><strong>Stockout</strong></div>
  </div>`,
  methods: {
      addCart(i){
        if(!this.product.isCarted) {
          if (this.product.stock >= 1) {
            this.product.isCarted=true;
            this.$emit('carting',i);
          }
          else {
            alert("Stockout")
          }
        }
      }
  },
  created(){
    this.product.img_path = 'static/images/products/'+this.product.product_id + '.png'

    var temp = JSON.parse(localStorage.getItem(this.username)).find((item) => item.product_id === this.product.product_id);
    if (temp) {
      this.product.isCarted = temp.isCarted
    }
    else {
      this.product.isCarted = false
    }
  },
  updated(){
    this.product.img_path = 'static/images/products/'+this.product.product_id + '.png'

    var temp = JSON.parse(localStorage.getItem(this.username)).find((item) => item.product_id === this.product.product_id);
    if (temp) {
      this.product.isCarted = temp.isCarted
    }
    else {
      this.product.isCarted = false
    }
  }
}) 
Vue.component('cart-item',{
  props:['product'],
  template: `
  <div class="row">
    <div class="col">
      [[product.product_name]]
    </div>
    <div class="col">
    <i class="bi bi-currency-rupee"></i> [[calculateTotal]]
    </div>
    <div class="col">
      <input type="number" v-model="product.qty" class="form-control" aria-label="Qty" @change="changeHandler">
    </div>
  </div>`,
  methods: {
    removeFromCart(i){
      this.product.isCarted = false;
      this.$emit('decarting',i);
    },
    updateLocalStore() {
      // alert('emiting')
      this.$emit('updateqty');

    },
    changeHandler(){
      if (this.product.qty == 0){
        this.removeFromCart(this.product);
      }
      if (this.product.qty > this.product.stock){
        alert("Stockout Imminent");
        this.product.qty = this.product.stock
      }
      this.updateLocalStore()
    }
  },
  computed: {
    calculateTotal() {
      return this.product.qty * this.product.price;
    }
  }
})


new Vue({
  el: '#app',
  data: {
    sections: [],
    cartItems: [], 
    cartMinimized: true,
    total: 0,
    user: {},
    search: {
      name: '',
      qSection: '',
      maxPrice: '',
      minPrice: '',
      mfd: '',
      expd: '',
    },
    results: []
  },
  methods: {
    dataFetcher() {
      fetch('http://127.0.0.1:8080/api/section/all')
      .then(response => response.json())
      .then(data => {
        this.sections = data;
        if (localStorage.getItem(this.user.username)){
          this.cartItems = JSON.parse(localStorage.getItem(this.user.username));
        }
        else{
          localStorage.setItem(this.user.username,JSON.stringify(this.cartItems));
        }
        // console.log(this.sections)
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      })
    },
    addToCart(item) {
      item.qty = 1;
      this.cartItems.push(item);
      localStorage.setItem(this.user.username,JSON.stringify(this.cartItems));
      // alert(localStorage.getItem(this.user.username))
      this.dataFetcher()
      
    },
    removeFromCart(product) {
      const index = this.cartItems.indexOf(product);
      if (index > -1) {
        this.cartItems.splice(index, 1);
      }
      localStorage.setItem(this.user.username,JSON.stringify(this.cartItems));
      this.dataFetcher();
    },
    updateLocalStore() {
      localStorage.setItem(this.user.username,JSON.stringify(this.cartItems));
      // alert('updated')
      // alert(localStorage.getItem(this.user.username))
    },
    confirmBuy() {
      alert('Placing Order...');
      // alert(JSON.stringify(this.cartItems));
      var order = ''
      this.cartItems.forEach(obj => {
        order = order + obj.qty + "_x_" + obj.product_name.replace(' ', '_') + "+" 
      })
      // alert(order)
      fetch(`http://127.0.0.1:8080/checkout/${order}`)
      .then(response => response.json())
      .then(data => alert(data.data))
      .catch(error => {
        console.error('Error fetching data:', error);
      })

      this.cartItems = []
      localStorage.setItem(this.user.username,JSON.stringify(this.cartItems));
      this.dataFetcher();
    },
    minimizeCart() {
      this.cartMinimized = !this.cartMinimized;
    },
    expandCart() {
      this.cartMinimized = false;
    },
		searchProduct() {
      var query = 'http://127.0.0.1:8080/api/product/all'
      if (this.search.name != null) {
        query += `?name=${this.search.name}`
      }
      if (this.search.expd != null) {
        query += `&expd=${this.search.expd}`
      }
      if (this.search.mfd != null) {
        query += `&mfd=${this.search.mfd}`
      }
      if (this.search.maxPrice != null) {
        query += `&maxPrice=${this.search.maxPrice}`
      }
      if (this.search.minPrice != null) {
        query += `&minPrice=${this.search.minPrice}`
      }
      if (this.search.qSection != null) {
        query += `&qSection=${this.search.qSection}`
      }
      // alert(query)
      fetch(query)
      .then(response => response.json())
      .then(data => {
        // alert('working')
        // console.log(data)
        this.results = data
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      })
      // alert('here')
		}
  },
  computed:{
    calculateTotal() {
      return this.cartItems.reduce((total, item) => {
        return total + (item.price * item.qty);
      }, 0);
    },
  },
  created(){
    fetch('http://127.0.0.1:8080/get-users/this')
    .then(response => response.json())
    .then(data => {
      this.user = data
    })
    this.dataFetcher();
  }
});