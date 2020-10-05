import axios from 'axios';
import React from 'react';
import ReactDOM from 'react-dom';
import regeneratorRuntime from 'regenerator-runtime';
import NewPostModal from '../components/NewPostModal';
import Thread from '../components/Thread';
import { reducer, newPost, DEFAULT_STATE } from '../state';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

const initialState = window._STORE;
const store = createStore(reducer, initialState);


async function fetchPost(postId) {
    let endpoint = '/api/v1/post/' + postId;
    let response = await axios.get(endpoint);
    console.log('response:');
    console.log(response);
    let postData = response.data;
    return postData;
}

async function eventLoop() {
    if(!!window.SharedWorker) {
        let workerUrl = window._LIVE_PROXY;
        let liveProxy = new SharedWorker(workerUrl);
        
        liveProxy.port.onmessage = async function(e) {
            let data = e.data;
            switch(data.message) {
            case 'new-post':
                let post = await fetchPost(data.post);
                console.log('new post:');
                console.log(post);
                store.dispatch(newPost(post));
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
}
eventLoop();
ReactDOM.hydrate(<React.Fragment>
                   <Provider store={store}>
                     <NewPostModal thread_id={window._THREAD} embed_submit={true}/>
                     <Thread />
                   </Provider>
                 </React.Fragment>, document.getElementById('thread-container'));
