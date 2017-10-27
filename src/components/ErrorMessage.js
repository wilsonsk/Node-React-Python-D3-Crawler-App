import React from 'react';

class ErrorMessage extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            error: this.props.errorMessage
        };
    }
    
    componentWillReceiveProps(nextProps) {
        if (this.props.errorMessage !== nextProps.errorMessage) {
            this.state.error = nextProps.errorMessage;
        }
        console.log("ErrorMessage nextProps: " + nextProps.errorMessage);
    }
    
    render() {
        if (this.props.errorMessage == '') {
            return(
                <p></p>
            )
        }
        return(
            <p className="col-sm-8 error-message">{this.state.error}</p>
        )
    }
}

export default ErrorMessage;