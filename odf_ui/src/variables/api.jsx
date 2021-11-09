import axios from 'axios';
import queryString from 'query-string'


export const get_resource = (data, callback) => {
    let attrs = Object.entries(data).map(
        e => e[1].attrs).filter(e => e).flatMap(e => e);
    console.log(attrs);
    if (attrs.length > 0) {
        let ids = new Set(attrs.map(e => e.item_id[0]));
        let obj_type = attrs[0].item_type[0];
        axios.get('/api/' + obj_type.toLowerCase() + '/get_by_id', {
            params: {
                id: Array.from(ids),
                stored_field_only: true,
            },
            paramsSerializer: (params) => queryString.stringify(params, { arrayFormat: 'repeat' })
        }).then(r => {
            let map = {};
            for (let d of r.data)
                map[d._id] = d;
            callback(map);
        })
    }
}