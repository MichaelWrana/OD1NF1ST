import React, { memo } from 'react';
import { Handle } from 'react-flow-renderer';



export default memo(({ data }) => {
    return (
        <div className="GC" >
            <Handle
                type="target"
                position="left"
                style={{ background: '#555' }}
                onConnect={(params) => console.log('handle onConnect', params)}
            />
            <div>
                {data.label}
            </div>
            <div>
                {data.sources ? `${data.sources.length} sources` : ''}
            </div>
            <div>{ }</div>
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