import React from 'react';
import ReactDOM from 'react-dom';
import Catalog from '../components/Catalog';
import { reducer, DEFAULT_STATE } from '../state';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

const initialState = window._STORE;
const store = createStore(reducer, initialState);

ReactDOM.hydrate(<Provider store={store}>
                   <Catalog />
                 </Provider>, document.getElementById('catalog-root'));
