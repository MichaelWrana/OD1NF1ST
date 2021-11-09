import React, { memo } from 'react';
import { Handle } from 'react-flow-renderer';
import { useEffect } from 'react';
import { useState } from 'react';
import { ax } from '../../api';
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
const bgs = {
    'State.IDEL': '#f5f5f5',
    'State.TRANSMIT': '#26c6da',
    'State.RECEIVE': '#ba68c8',
    'State.OFF': '#f5f5f5',
    'State.WAIT': '#69f0ae',
    'State.TRANSMIT_CMD': '#f5f5f5',
}
var attack_vals = []
ax.get('api/list_attacks').then(res => {
    if (res.data) attack_vals = res.data;
    console.log(attack_vals)
})
export default memo(({ data }) => {
    const [attacks, setAttacks] = useState(attack_vals);
    return (
        <div className="RT" style={{ backgroundColor: bgs[data.state] }}>
            <Handle
                type="target"
                position="left"
                style={{ background: '#555' }}
                onConnect={(params) => console.log('handle onConnect', params)}
            />
            <div>
                {data.mode.substring(5) + ' - ' + data.state.substring(6)}
            </div>
            <div>
                {data.label}
            </div>
            <div>
                <UncontrolledDropdown>
                    <DropdownToggle caret data-toggle="dropdown" className="btn-sm btn-danger">
                        Sabotage
                    </DropdownToggle>
                    <DropdownMenu className="dropdown-black">
                        {attacks.filter(v => v.args.target == "-1").map((v, k) =>
                            <DropdownItem key={k} title={v} onClick={
                                () => {
                                    let args = {};
                                    Object.assign(args, v.args);
                                    args.target = data.address;
                                    ax.post('api/sabotage/' + v.class, args)//.then(() => alert('Attack launched'))
                                }
                            }>
                                <div>
                                    <i className="tim-icons icon-controller text-success" />{v.name}
                                </div>
                                {/* {v.description} */}
                            </DropdownItem>
                        )}
                    </DropdownMenu>
                </UncontrolledDropdown>
            </div>
            <Handle
                type="source"
                position="right"
                // id="a"
                style={{ background: '#555' }}
            />
            {/* <Handle
                type="source"
                position="right"
                id="b"
                style={{ bottom: 10, top: 'auto', background: '#555' }}
            /> */}
        </div>
    );
});