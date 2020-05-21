import React from 'react';
import ReactDOMServer from 'react-dom/server';
import Catalog from './components/Catalog';
import Post from './components/Post';
import Thread from './components/Thread';

const express = require('express');
const app = express();
app.use(express.json());
const port = 3000;



app.get('/health-check', (req, res) => res.send('OK'));
app.post('/render/catalog', function (req, res) {
    const catalog = req.body.data;
    const template = req.body.template;
    const template_with_data = template.replace('CATALOG_DATA', JSON.stringify(catalog)); 
    return res.send(template_with_data.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Catalog {...catalog}/>)));
});
app.post('/render/thread', function (req, res) {
    const thread = req.body.data;
    const template = req.body.template;
    const template_with_data = template.replace('THREAD_DATA', JSON.stringify(thread));
    return res.send(template_with_data.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Thread {...thread}/>)));
});
app.post('/render/post', function (req, res) {
    const post = req.body.data;
    const template = req.body.template;
    return res.send(template.replace('TEMPLATE_CONTENT', ReactDOMServer.renderToString(<Post {...post}/>)));
});

app.listen(port, () => console.log(`Render server started on port ${port}`));
