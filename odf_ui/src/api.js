import axios from 'axios';
export const host = 'http://127.0.0.1:8572/'
// export const host = '/'
const axiosConfig = {
    baseURL: host,
    timeout: 30000,
};

export const urlfor = res => host + res

export const ax = axios.create(axiosConfig)