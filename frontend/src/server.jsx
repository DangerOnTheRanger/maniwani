import React from 'react';
import ReactDOMServer from 'react-dom/server';
import Catalog from './components/Catalog';
import Post from './components/Post';
import Thread from './components/Thread';
import { reducer, setBoard, setStyles, DEFAULT_STATE } from './state';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

const express = require('express');
const app = express();
app.use(express.json());
const port = 3000;


app.get('/health-check', (req, res) => res.send('OK'));
function serveCatalog(req, res) {
    const catalog = req.body.data.catalog;
    const boardId = req.body.data.board_id;
    const initialState = Object.assign({}, DEFAULT_STATE, {threads: catalog.threads});
    const store = createStore(reducer, initialState);
    store.dispatch(setBoard(catalog.display_board));
    store.dispatch(setStyles(catalog.tag_styles));
    const template = req.body.template;
    const template_with_data = template.replace('STORE_DATA',
                                                JSON.stringify(store.getState())).
          replace('BOARD_ID', boardId);
    var serverDOM = ReactDOMServer.renderToString(<Provider store={store}>
                                                    <Catalog />
                                                  </Provider>);
    return res.send(template_with_data.replace('TEMPLATE_CONTENT', serverDOM));
}
app.post('/render/catalog', serveCatalog);
function serveThread(req, res) {
    const thread = req.body.data.thread;
    const threadId = req.body.data.thread_id;
    const initialState = Object.assign({}, DEFAULT_STATE, {posts: thread.posts});
    const store = createStore(reducer, initialState);
    const template = req.body.template;
    const template_with_data = template.replace('STORE_DATA',
                                                JSON.stringify(store.getState())).
          replace('THREAD_ID', threadId);
    var serverDOM = ReactDOMServer.renderToString(<Provider store={store}>
                                                    <Thread />
                                                  </Provider>);
    return res.send(template_with_data.replace('TEMPLATE_CONTENT', serverDOM));
}
app.post('/render/thread', serveThread);
app.post('/render/post', function (req, res) {
    const post = req.body.data;
    const template = req.body.template;
    return res.send(template.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Post {...post}/>)));
});

app.listen(port, () => console.log(`Render server started on port ${port}`));
