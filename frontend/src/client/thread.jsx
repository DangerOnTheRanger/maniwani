import React from 'react';
import ReactDOM from 'react-dom';
import Thread from '../components/Thread';
import { reducer, newPost, DEFAULT_STATE } from '../state';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

const initialState = window._STORE;
const store = createStore(reducer, initialState);
if(!!window.SharedWorker) {
    let workerUrl = window._LIVE_PROXY;
    var liveProxy = new SharedWorker(workerUrl);
    
    liveProxy.port.onmessage = function(e) {
        let data = e.data;
        switch(data.message) {
        case 'new-post':
            store.dispatch(newPost(data.post));
            break;
        case 'debug':
            console.log(data.content);
            break;
        }
    };

    const threadId = window._THREAD;
    liveProxy.port.postMessage({'message': 'subscribe-thread', 'thread': threadId});
    console.log('thread ID: ' + threadId);
}
ReactDOM.hydrate(<Provider store={store}>
                   <Thread />
                 </Provider>, document.getElementById('thread-container'));
