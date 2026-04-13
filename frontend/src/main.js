import { createApp } from 'vue'
import App from './App.vue'
import router from './router'


const app = createApp(App)

app.use(router)
app.mount('#app')

window.getCSRFToken = function() {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; csrftoken=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}


window.csrfFetch = async function(url, options = {}) {
  const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
  const method = (options.method || 'GET').toUpperCase();

  if (!safeMethods.includes(method)) {
    const token = window.getCSRFToken();
    if (!options.headers) options.headers = {};
    options.headers['X-CSRFToken'] = token;
  }

  options.credentials = 'include';
  return fetch(url, options);
}
