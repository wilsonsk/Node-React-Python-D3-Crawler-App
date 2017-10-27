import React from 'react';
import io from 'socket.io-client';

class Results extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            data: this.props.displayMessage
        };
    }
    
    componentWillReceiveProps(nextProps) {
        if (this.props.displayMessage !== nextProps.displayMessage) {
            this.state.data = nextProps.displayMessage;
        }
    }
    
    render() {
        return(
            <div className="container " id="results">
                <textarea rows="20" cols="150" className="text-display" value={this.state.data} readOnly/>
            </div>
        )
    }
}

export default Results;