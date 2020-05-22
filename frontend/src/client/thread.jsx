import React from 'react';
import ReactDOM from 'react-dom';
import Thread from '../components/Thread';
import { reducer, DEFAULT_STATE } from '../state';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

const initialState = window._STORE;
const store = createStore(reducer, initialState);
ReactDOM.hydrate(<Provider store={store}>
                   <Thread />
                 </Provider>, document.getElementById('thread-container'));
