import React from 'react';
import io from 'socket.io-client';

class Cookies extends React.Component {
    constructor(props) {
        super(props);
        
        // data needs to be a string in the constructor instead of an object
        var crawlArgs = '';
        var previousSearch = false;
        
        if(this.props.cookieCrawlArgs){
          crawlArgs = this.props.cookieCrawlArgs;
          previousSearch = true;
        }
        
        this.state = {
            args: crawlArgs,
            currentArg: this.props.cookieCrawlArgs ? this.props.cookieCrawlArgs[0] : '',
            data: '',
            previousSearch: previousSearch
        };
        
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    
    handleInputChange(event) {
        const target = event.target;
        const value = target.value;
        const name = target.name;
        
        this.setState({[name]: value});
        this.props.updateDisplay("Crawling with args: '" + this.state.currentArg + "'");
    }
    
    handleSubmit(event) {
        event.preventDefault();
        const socket = io.connect();
        
        if (!this.props.cookieCrawlArgs) {
          return;
        }
        
        else {
          // send arguments to crawler via server
          socket.emit('start crawl', this.state.currentArg);
          this.props.updateDisplay("Crawling with args: '" + this.state.currentArg + "'");
  
          // crawl completes with a validated URL
          socket.on('crawl data available', (data) => {
              this.state.data = data;
              
              // Update displayMessage in App.js
              this.props.updateCrawlResults(this.state.data);
              this.props.updateDisplay(this.state.data);
          });
          
          //close socket connection
          //socket.emit('force disconnect');
        }
    }
    
    render() {
        var options = [];
        if (!this.props.cookieCrawlArgs) {
          options.push(<option key={1}>"You have no saved crawls."</option>);
        }
        
        else {
          for (var i = 0; i < this.props.cookieCrawlArgs.length; i++) {
             options.push(<option key={i} name="currentArg" value={this.props.cookieCrawlArgs[i]}>{this.props.cookieCrawlArgs[i]}</option>);
          }
        }
        
        return(
            <div className="container theme-showcase head first-jumbotron" role="main">
              <div className="jumbotron">
                <form className="form-horizontal" onSubmit={this.handleSubmit}>
                  <div className="form-group">
                    <label className="control-label col-sm-2" htmlFor="saved">Saved Crawls:</label>
                    <div className="col-sm-6">
                      <select className="form-control" name="currentArg" onChange={this.handleInputChange}>
                        {options}
                      </select>
                    </div>
                  </div>
                  <div className="form-group">
                    <div className="col-sm-offset-2 col-sm-10">
                      <button type="submit" className="btn btn-default">Crawl Again</button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
        )
    }
}

export default Cookies;