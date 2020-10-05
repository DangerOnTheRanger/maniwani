import express from 'express';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import BoardIndex from './components/BoardIndex';
import Catalog from './components/Catalog';
import { NewPostForm, NewThreadForm } from './components/PostForm';
import NewPostModal from './components/NewPostModal';
import NewThreadModal from './components/NewThreadModal';
import Post from './components/Post';
import Thread from './components/Thread';
import ThreadGallery from './components/ThreadGallery';
import { reducer, setBoard, setStyles, setCaptcha, DEFAULT_STATE } from './state';
import { createStore } from 'redux';
import { Provider } from 'react-redux';


const app = express();
// need to increase the limit for the sake of potential embedded captchas
app.use(express.json({limit: '3mb', extended: true}));
const port = 3000;


function extractCaptcha(reqBody) {
    if(reqBody.data.captcha_method == 'CAPTCHOULI') {
        return {
            captcha_method: reqBody.data.captcha_method,
            captcha_id: reqBody.data.captchouli.captcha_id,
            character: reqBody.data.captchouli.character,
            images: reqBody.data.captchouli.images,
        };
    }
    return {};
}

app.get('/health-check', (req, res) => res.send('OK'));
function serveCatalog(req, res) {
    const catalog = req.body.data.catalog;
    const boardId = req.body.data.board_id;
    const captchaProps = extractCaptcha(req.body);
    const initialState = Object.assign({}, DEFAULT_STATE, {threads: catalog.threads});
    const store = createStore(reducer, initialState);
    store.dispatch(setStyles(catalog.tag_styles));
    store.dispatch(setCaptcha(extractCaptcha(req.body)));
    const template = req.body.template;
    const templateWithData = template.replace('STORE_DATA',
                                                JSON.stringify(store.getState())).
          replace('BOARD_ID', boardId);
    var serverDOM = ReactDOMServer.renderToString(<Provider store={store}>
                                                    <NewThreadModal board_id={boardId} embed_submit={true}/>
                                                    <Catalog display_board={false} />
                                                  </Provider>);
    return res.send(templateWithData.replace('TEMPLATE_CONTENT', serverDOM));
}
app.post('/render/catalog', serveCatalog);
app.post('/render/board-index', function (req, res) {
    const boards = req.body.data.boards;
    const serverDOM = ReactDOMServer.renderToString(<BoardIndex boards={boards}/>);
    const template = req.body.template;
    return res.send(template.replace('TEMPLATE_CONTENT', serverDOM));
    
}); 
function serveThread(req, res) {
    const thread = req.body.data.thread;
    const threadId = req.body.data.thread_id;
    const captchaProps = extractCaptcha(req.body);
    const initialState = Object.assign({}, DEFAULT_STATE, {posts: thread.posts});
    const store = createStore(reducer, initialState);
    store.dispatch(setCaptcha(extractCaptcha(req.body)));
    const template = req.body.template;
    const templateWithData = template.replace('STORE_DATA',
                                                JSON.stringify(store.getState())).
          replace('THREAD_ID', threadId);
    var serverDOM = ReactDOMServer.renderToString(<React.Fragment>
                                                    <Provider store={store}>
                                                      <NewPostModal thread_id={threadId} embed_submit={true}/>
                                                      <Thread />
                                                    </Provider>
                                                  </React.Fragment>);
    return res.send(templateWithData.replace('TEMPLATE_CONTENT', serverDOM));
}
app.post('/render/thread', serveThread);
app.post('/render/post', function (req, res) {
    const post = req.body.data;
    const template = req.body.template;
    return res.send(template.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Post {...post}/>)));
});
app.post('/render/firehose', function (req, res) {
    const firehose = req.body.data.firehose;
    const initialState = Object.assign({}, DEFAULT_STATE, {threads: firehose.threads});
    const store = createStore(reducer, initialState);
    store.dispatch(setStyles(firehose.tag_styles));
    const template = req.body.template;
    var serverDOM = ReactDOMServer.renderToString(<Provider store={store}>
                                                    <Catalog display_board={true} />
                                                  </Provider>);
    return res.send(template.replace('TEMPLATE_CONTENT', serverDOM));
});

app.post('/render/new-thread', function (req, res) {
    const boardId = req.body.data.board_id;
    const captchaProps = extractCaptcha(req.body);
    const template = req.body.template;
    const serverDOM = ReactDOMServer.renderToString(<NewThreadForm action="/threads/new" board_id={boardId} embed_submit={true} {...captchaProps}/>);
    return res.send(template.replace('TEMPLATE_CONTENT', serverDOM));
});

app.post('/render/new-post', function (req, res) {
    const threadId = req.body.data.thread_id;
    const captchaProps = extractCaptcha(req.body);
    const template = req.body.template;
    const serverDOM = ReactDOMServer.renderToString(<NewPostForm action={"/threads/" + threadId + "/new"} thread_id={threadId} embed_submit={true} {...captchaProps}/>);
    return res.send(template.replace('TEMPLATE_CONTENT', serverDOM));
});

app.post('/render/gallery', function (req, res) {
    const posts = req.body.data.posts;
    const template = req.body.template;
    const serverDOM = ReactDOMServer.renderToString(<ThreadGallery posts={posts}/>);
    return res.send(template.replace('TEMPLATE_CONTENT', serverDOM));
});

app.listen(port, () => console.log(`Render server started on port ${port}`));
