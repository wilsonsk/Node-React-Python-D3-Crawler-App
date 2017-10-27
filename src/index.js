import React from 'react';
import ReactDOM from 'react-dom';

import App from './components/App';

ReactDOM.render(
  <App cookieCrawlData={window.cookieCrawlData} cookieCrawlHistory={window.cookieCrawlHistory} cookieCrawlArgs={window.cookieCrawlArgs} />,
  document.getElementById('root')
);





