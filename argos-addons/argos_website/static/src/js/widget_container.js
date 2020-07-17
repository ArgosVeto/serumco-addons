/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./assets/js/widget-container.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./assets/js/widget-container.js":
/*!***************************************!*\
  !*** ./assets/js/widget-container.js ***!
  \***************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("function init() {\n  var container = document.querySelector('#vetowidget');\n\n  if (!container) {\n    return;\n  }\n\n  var scriptElement = document.querySelector('[data-widget-clinic]');\n  var clinic = parseInt(scriptElement.dataset.widgetClinic, 10);\n  var iframe = document.createElement('iframe');\n  iframe.style.border = 'none';\n  iframe.style.width = '100%';\n  iframe.style.height = '500px';\n  container.appendChild(iframe);\n  var html = \"\\n    <body>\\n        <div id=\\\"vetowidget\\\"></div>\\n        <script>\\n            const globalVars = {\\n                clinic: \".concat(clinic, \",\\n                url: 'http://recette.monrendezvousveto.fr'\\n            };\\n        </script>\\n        <script src=\\\"http://recette.monrendezvousveto.fr/bundles/app/assets/js/widget.entry.js\\\"></script>\\n    </body>\\n    \");\n  iframe.contentWindow.document.open();\n  iframe.contentWindow.document.write(html);\n  iframe.contentWindow.document.close();\n  iframe.contentWindow.addEventListener('mounted', function () {\n    resizeIFrameToFitContent(iframe);\n  });\n}\n\nfunction resizeIFrameToFitContent(iframe) {\n  iframe.height = iframe.contentWindow.document.body.scrollHeight;\n}\n\ninit();\n\n//# sourceURL=webpack:///./assets/js/widget-container.js?");

/***/ })

/******/ });