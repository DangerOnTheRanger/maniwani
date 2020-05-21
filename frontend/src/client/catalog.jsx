import React from 'react';
import ReactDOM from 'react-dom';
import Catalog from '../components/Catalog';

const catalog_data = window._CATALOG;
ReactDOM.hydrate(<Catalog {...catalog_data} />, document.getElementById('catalog-root'));
