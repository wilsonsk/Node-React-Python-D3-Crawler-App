import React from 'react';

class Timer extends React.Component {
    constructor(props) {
        super(props);
    }
    
    render() {
        return(
            <div className="container theme-showcase head" role="main">
              <div className="jumbotron">
                <p>Timer</p>
              </div>
            </div>
        )
    }
}

export default Timer;