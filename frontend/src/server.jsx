import React from 'react';
import ReactDOMServer from 'react-dom/server';
import Catalog from './components/Catalog';
import Post from './components/Post';
import Thread from './components/Thread';

const express = require('express');
const app = express();
app.use(express.json());
const port = 3000;



app.get('/', (req, res) => res.send('Hello World!'));
app.post('/render/catalog', function (req, res) {
    console.log("req.body:");
    console.log(req.body);
    const catalog = req.body.data;
    const template = req.body.template;
    return res.send(template.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Catalog {...catalog}/>)));
});
app.post('/render/thread', function (req, res) {
    const thread = req.body.data;
    const template = req.body.template;
    return res.send(template.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Thread {...thread}/>)));
});
app.post('/render/post', function (req, res) {
    const post = req.body.data;
    const template = req.body.template;
    return res.send(template.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Post {...post}/>)));
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`));
