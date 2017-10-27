import React from 'react';
import Navbar from './Navbar';
import Cookies from './Cookies';
import ErrorMessage from "./ErrorMessage";
import Instructions from './Instructions';
import Timer from './Timer';
import InputForm from './InputForm';
import Visualization from './Visualization';
import Results from './Results';
import Footer from './Footer';

import PropTypes from 'prop-types';

class App extends React.Component {
    static propTypes = {
      cookieCrawlData: PropTypes.string,
      crawlHistory: PropTypes.string,
      cookieCrawlArgs: PropTypes.string
    };
    
    constructor(props) {
        super(props);
        
        this.state = {
            crawlResults: this.props.cookieCrawlData,
            crawlHistory: this.props.cookieCrawlHistory,
            crawlArgs: this.props.cookieCrawlArgs,
            displayMessage: '',
            errorMessage: ''
        };
        
        this.updateCrawlResults = this.updateCrawlResults.bind(this);
        this.updateErrorMessage = this.updateErrorMessage.bind(this);
        this.updateDisplay = this.updateDisplay.bind(this);
        this.updateCookieList = this.updateCookieList.bind(this);
        
    }
    
    updateCrawlResults(newResult) {
        this.setState({ crawlResults: newResult});
    }
    
    updateErrorMessage(newError) {
        this.setState({ errorMessage: newError});
    }
    
    updateDisplay(newMessage) {
        this.setState({ displayMessage: newMessage});
    }
    
    updateCookieList(newArgs) {
        var argsList;
        if (this.state.crawlArgs === "") {
            argsList = [];
        } else {
            var argsList = this.state.crawlArgs.slice();
        }
        argsList.push(newArgs);
        this.setState({ crawlArgs: argsList });
    }
    
    render() {
        return(
            <div className="container">
                <Navbar />
                {/*<Instructions />*/}
                <Cookies cookieCrawlArgs={this.state.crawlArgs} 
                    updateDisplay={this.updateDisplay} 
                    updateCrawlResults={this.updateCrawlResults}/>
                <InputForm 
                    updateCrawlResults={this.updateCrawlResults} 
                    updateErrorMessage={this.updateErrorMessage} 
                    updateDisplay={this.updateDisplay} 
                    errorMessage={this.state.errorMessage}  
                    updateCookieList={this.updateCookieList}/>
                <Visualization crawlResults={this.state.crawlResults} />
                <Results displayMessage={this.state.displayMessage} />
                <Footer />
            </div>
        );
    }
}

export default App;