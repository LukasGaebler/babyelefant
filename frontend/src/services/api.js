import axios from 'axios'
export default axios.create({
    baseURL: `https://pressler.dev:8080`,
});