import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// PrimeVue imports
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

// PrimeVue components
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import Card from 'primevue/card'
import Menu from 'primevue/menu'
import Menubar from 'primevue/menubar'
import Avatar from 'primevue/avatar'
import Badge from 'primevue/badge'
import Ripple from 'primevue/ripple'
import StyleClass from 'primevue/styleclass'

// PrimeVue styles
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

// Custom styles
import './assets/styles/layout.scss'

const app = createApp(App)

// Pinia store
app.use(createPinia())

// Vue Router
app.use(router)

// PrimeVue
app.use(PrimeVue, { ripple: true })
app.use(ToastService)
app.use(ConfirmationService)

// PrimeVue components
app.component('Button', Button)
app.component('InputText', InputText)
app.component('Password', Password)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.component('Card', Card)
app.component('Menu', Menu)
app.component('Menubar', Menubar)
app.component('Avatar', Avatar)
app.component('Badge', Badge)

// PrimeVue directives
app.directive('ripple', Ripple)
app.directive('styleclass', StyleClass)

app.mount('#app')
