import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import SSComparison from './SSComparison';
import TracksMap from './TracksMap';
import * as serviceWorker from './serviceWorker';

// ReactDOM.render(<SSComparison />, document.getElementById('root'));
ReactDOM.render(<TracksMap />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
