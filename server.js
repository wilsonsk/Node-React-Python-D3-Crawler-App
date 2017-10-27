//
// # NodeJS-React-Mongodb-webcrawler
//
// The syntax for operating the crawler right now is "python crawler.py <starting_url> -d". This will do a DFS crawl of 10 pages
// To change the page count, add "-l <page_count>" to the end of the previous string
//

// const URL = require('url').URL;
var crawler = "./crawler/crawler.py";
import config from './config';
import express from 'express';
const server = express();
var socketio = require('socket.io');

//url validation
var request = require('request');
var URL = require('url');
var validation = require('valid-url');

//cookie session
var session = require('express-session');
const MongoStore = require('connect-mongo')(session);
var sessionMiddleware = session({
    secret: 'andromeda', 
    store: new MongoStore({
      url: config.mongodbUri,
      ttl: 30 * 24 * 60 * 60,
      autoRemove: 'native'
    }),
    resave: true,
    saveUninitialized: true
});

server.set('view engine', 'ejs');

var socketServer = server.listen(config.port, () => {
  console.log('Express is listening on port ' + config.port);
});

var io = socketio.listen(socketServer);
io.use(function(socket, next){
	sessionMiddleware(socket.request, socket.request.res, next);
});
server.use(sessionMiddleware);

const exec = require('child_process').exec;

//Session Cookie IO route -- this route is set up for situation where the crawl data is only rendered on the submit button -- if we want cookie data to re render on page refresh or 'back button' we need to change the sockets on the inputform component
io.on('connection', (socket) => {
  var valid = false;
  socket.on('url available', (url) => {
    socket.request.session.url = url;
  });

  socket.on('start crawl', (args) => { 
    var parsedUrl = URL.parse(socket.request.session.url);
    
    parsedUrl.protocol = "http";
    var tempUrl = parsedUrl.protocol + "://" + parsedUrl.href;
    console.log(tempUrl);
    if(validation.isUri(tempUrl)){
      //more thorough ulr validation in crawler.py
      //session cookie
      if(socket.request.session.crawlData && socket.request.session.args){
        console.log("PREVIOUS SESSION DATA");
        console.log("client: start crawl");
        var child = exec('python ' + crawler + ' ' + args, {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
        // var child = exec('python ' + crawler + ' ' + 'ww.google.com -x', {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
          if(stderr){
	          socket.emit('error message', (stderr));
            console.error(stderr);
          }
          if(stdout){
            socket.request.session.args.push(args);
            console.log("DEBUG: " + socket.request.session.args);
            socket.request.session.crawlData.push(stdout);
            socket.request.session.save();
            console.log("Socket Session - PRINTING CRAWL HISTORY: \n" + socket.request.session.crawlData);
            socket.emit('crawl data available', (stdout));   
          }
        });   
      }else{
        console.log("NO SESSION DATA: NEW CRAWL");
        console.log("client: start crawl");
        var child = exec('python ' + crawler + ' ' + args, {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
        // var child = exec('python ' + crawler + ' ' + 'ww.google.com -x', {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
          if(stderr){
            socket.emit('error message', (stderr));
            console.error(stderr);
          }
          if(stdout){
            socket.request.session.args = [];
            socket.request.session.crawlData = [];
            socket.request.session.args.push(args);
            socket.request.session.crawlData.push(stdout);
            socket.request.session.save();
            console.log("Socket Session: \n" + socket.request.session.crawlData);
            socket.emit('crawl data available', (stdout));
          }
        });     
      }
    }else{
      parsedUrl.protocol = "https";
      var tempUrl = parsedUrl.protocol + "://" + parsedUrl.href;
      console.log(tempUrl);
      if(validation.isUri(tempUrl)){
        //more thorough url validation in crawler.py
            //session cookie
        if(socket.request.session.crawlData && socket.request.session.args){
          console.log("PREVIOUS SESSION DATA");
          console.log("client: start crawl");
          var child = exec('python ' + crawler + ' ' + args, {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
          // var child = exec('python ' + crawler + ' ' + 'ww.google.com -x', {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
            if(stderr){
  	          socket.emit('error message', (stderr));
              console.error(stderr);
            }
            if(stdout){
              socket.request.session.args.push(args);
              socket.request.session.crawlData.push(stdout);
              socket.request.session.save();
              console.log("Socket Session - PRINTING CRAWL HISTORY: \n" + socket.request.session.crawlData);
              socket.emit('crawl data available', (stdout));   
            }
          });   
        }else{
          console.log("NO SESSION DATA: NEW CRAWL");
          console.log("client: start crawl");
          var child = exec('python ' + crawler + ' ' + args, {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
          // var child = exec('python ' + crawler + ' ' + 'ww.google.com -x', {maxBuffer: 1024 * 500}, (error, stdout, stderr) => {
            if(stderr){
              socket.emit('error message', (stderr));
              console.error(stderr);
            }
            if(stdout){
              socket.request.session.args = [];
              socket.request.session.crawlData = [];
              socket.request.session.args.push(args);
              socket.request.session.crawlData.push(stdout);
              socket.request.session.save();
              console.log("Socket Session: \n" + socket.request.session.crawlData);
              socket.emit('crawl data available', (stdout));
            }
          });     
        }
      }else{
        socket.emit('error message', ('INVALID URL - ENTER A VALID URL'));
      }  
    }
  });
});

server.get('/', (req, res) => {
  if(req.session.crawlData){
    console.log("Session Req Previoulsy Established - PRINTING CRAWL HISTORY: " + req.session.crawlData.length + " crawls total \n" + req.session.crawlData);
    res.render('index', {
      cookieCrawlData: req.session.crawlData[req.session.crawlData.length - 1],
      cookieCrawlHistory: req.session.crawlData,
      cookieCrawlArgs: req.session.args
    });    
  }else{
    console.log("No Cookie Session Established Yet");
    res.render('index', {
      cookieCrawlData: "",
      cookieCrawlHistory: "",
      cookieCrawlArgs: ""
    });    
  }
});

// function validateUrl(url){
//   console.log("STARTING VALIDATE URL FUNCTION");
//   var valid = false;
//   var parsedUrl = URL.parse(url);
  
//   parsedUrl.protocol = "http";
//   var tempUrl = parsedUrl.protocol + "://" + parsedUrl.href;
//   console.log(tempUrl);
//   if(validation.isUri(tempUrl)){
//   // if(urlRegex().test(tempUrl)){
//     //make request as alternative to ping - find way to make header request (less overhead)
//     request(tempUrl, (err, res, body) => {
//       if(err){
        
//       }else{
//         console.log("REQ TRUE");
//         valid = true;
//       }
//     });
//   }else{
//     parsedUrl.protocol = "https";
//     var tempUrl = parsedUrl.protocol + "://" + parsedUrl.href;
//     console.log(tempUrl);
//     if(validation.isUri(tempUrl)){
//     // if(urlRegex().test(tempUrl)){
//       //make header request as alternative to ping
//       request(tempUrl, (err, res, body) => {
//         if(err){
          
//         }else{
//           console.log("REQ TRUE");
//           valid = true;
//         }
//       });
//     }else{
//       console.log("REQ FAIL");
//     }  
//   }
//   return valid;

// }

server.use(express.static('public'));


