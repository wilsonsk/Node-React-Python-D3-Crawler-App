import React from 'react';
import io from 'socket.io-client';
import ErrorMessage from './ErrorMessage';

//NOTE: if we want to have the cookie functionality where if the page is refreshed or user clicks back, etc., we need to add a socket.on in the constructor and push the cookie data into the data property of the state

class InputForm extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            data: '',
            depth: '10',
            error: '',
            keyword: '',
            type: 'd',
            url: ''
        };
        
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    
    handleInputChange(event) {
        const target = event.target;
        const value = target.value;
        const name = target.name;
        
        this.setState({[name]: value});
    }
    
    handleSubmit(event) {
        event.preventDefault();
        const socket = io.connect();
        var args = '';
        
        // clear error message
      	this.props.updateErrorMessage('');
        
        // submit url for validation
	      socket.emit('url available', (this.state.url));
        
        // build argument string
        args += this.state.url;
        args += ' -' + this.state.type;
        if (this.state.type === 'b')
            args += ' 3';
        args += ' -l ' + this.state.depth;
        if (this.state.keyword !== '') 
            args += ' -k ' + this.state.keyword;
        
        // send arguments to crawler via server
        socket.emit('start crawl', args);
        this.props.updateDisplay("Crawling with args: '" + args + "'");

      	// Crawler error status
      	socket.on('error message', (err) => {
      	    
      	    if (err == 1) {
      		      this.state.error = "Please enter a URL.";
      	    } else if (err == 2) {
      	        this.state.error = "The URL you entered is not valid. Please try again.";
      	    }
      
      		  this.props.updateErrorMessage(this.state.error);
      	});

        // crawl completes with a validated URL
        socket.on('crawl data available', (data) => {
            this.state.data = data;
            
            // Update crawlResults and displayMessage in App.js
            this.props.updateCrawlResults(this.state.data);
            this.props.updateDisplay(this.state.data);
            this.props.updateCookieList(args);
        });
        
        //close socket connection
        //socket.emit('force disconnect');
    }
    
    render(){
        return (
            <div className="container theme-showcase head" role="main">
              <div className="jumbotron">
                <form className="form-horizontal" onSubmit={this.handleSubmit}>
                  <div className="form-group">
                    <label className="control-label col-sm-2" htmlFor="url">Starting Website:</label>
                    <div className="col-sm-2">
                      <input className="form-control" type="text" name="url" value={this.state.url} onChange={this.handleInputChange} />
                    </div>
                    <ErrorMessage errorMessage={this.props.errorMessage} />
                  </div>
                  <div className="form-group">
                    <label className="control-label col-sm-2" htmlFor="type">Crawl Type:</label>
                    <div className="col-sm-2">
                      <select className="form-control col-sm-2" name="type" value={this.state.type} onChange={this.handleInputChange}>
                        <option value="b">Breadth First</option>
                        <option value="d">Depth First</option>
                      </select>
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="control-label col-sm-2" htmlFor="depth">Max Pages:</label>
                    <div className="col-sm-2">
                      <input className="form-control" type="number" max="1000" min="0" name="depth" value={this.state.depth} onChange={this.handleInputChange} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="control-label col-sm-2" htmlFor="keyword">Keyword:</label>
                    <div className="col-sm-2">
                      <input className="form-control" type="text" name="keyword" value={this.state.keyword} onChange={this.handleInputChange} />
                    </div>
                  </div>
                  <div className="form-group">
                    <div className="col-sm-offset-2 col-sm-10">
                      <button type="submit" className="btn btn-default">Crawl</button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
        )
    }
}

export default InputForm;
