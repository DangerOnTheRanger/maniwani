import axios from 'axios';
import React from 'react';
import ReactDOM from 'react-dom';
import regeneratorRuntime from 'regenerator-runtime';
import Catalog from '../components/Catalog';
import NewThreadModal from '../components/NewThreadModal';
import { reducer, newThread, deleteThread, DEFAULT_STATE } from '../state';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

const initialState = window._STORE;
const store = createStore(reducer, initialState);

async function fetchCatalog(boardId) {
    // why do we fetch the entire catalog every single time?
    // this avoids having to figure out on the client which thread got
    // bumped off the catalog (duplicating server-side logic) and avoids
    // ugly potential bugs where the client removes the wrong thread
    // due to race conditions triggered by the oldest thread on the board
    // updating just in time (thus the 2nd-oldest thread should be removed instead)
    // fetching the entire catalog is more bandwidth-intensive,
    // but much simpler and less error-prone
    let endpoint = '/api/v1/board/' + boardId + '/catalog';
    let response = await axios.get(endpoint);
    console.log('response:');
    console.log(response);
    let catalogData = response.data;
    return catalogData;
}

function diffStore(catalog) {
    let commands = new Array();
    let storeIds = new Set();
    let storeThreads = store.getState().threads;
    storeThreads.forEach(thread => storeIds.add(thread.id));
    for(let thread of catalog) {
        if(!storeIds.has(thread.id)) {
            // insert newThread commands at the beginning, this way
            // the newest thread will get added last since we already
            // receive the catalog over REST in newest-first order
            commands.unshift(newThread(thread));
        }
    }
    let catalogIds = new Set();
    catalog.forEach(thread => catalogIds.add(thread.id));
    for(let thread of storeThreads) {
        if(!catalogIds.has(thread.id)) {
            commands.push(deleteThread(thread.id));
        }
    }
    console.log('commands:');
    console.log(commands);
    return commands;
}

async function eventLoop() {
    if(!!window.SharedWorker) {
        let workerUrl = window._LIVE_PROXY;
        let liveProxy = new SharedWorker(workerUrl);

        liveProxy.port.onmessage = async function(e) {
            let data = e.data;
            switch(data.message) {
            case 'new-thread':
                let catalog = await fetchCatalog(data.board);
                let commands = diffStore(catalog);
                commands.forEach(command => store.dispatch(command));
                break;
            case 'debug':
                console.log(data.content);
                break;
            }
        };
        const boardId = window._BOARD;
        liveProxy.port.postMessage({'message': 'subscribe-board', 'board': boardId});
        console.log('board ID: ' + boardId);
    }
}
eventLoop();
ReactDOM.hydrate(<React.Fragment>
                   <NewThreadModal board_id={window._BOARD} embed_submit={true}/>
                   <Provider store={store}>
                     <Catalog />
                   </Provider>
                 </React.Fragment>, document.getElementById('catalog-root'));
