var design;(()=>{var e={209:()=>{document.addEventListener("DOMContentLoaded",(()=>{document.querySelectorAll(".navbar-burger").forEach((e=>{e.addEventListener("click",(()=>{const t=e.dataset.target,n=document.getElementById(t);e.classList.toggle("is-active"),n.classList.toggle("is-active")}))})),document.querySelectorAll(".notification .delete").forEach((e=>{const t=e.parentNode;e.addEventListener("click",(()=>{t.parentNode.removeChild(t)}))}))}))}},t={};function n(o){var c=t[o];if(void 0!==c)return c.exports;var d=t[o]={exports:{}};return e[o](d,d.exports,n),d.exports}n.d=(e,t)=>{for(var o in t)n.o(t,o)&&!n.o(e,o)&&Object.defineProperty(e,o,{enumerable:!0,get:t[o]})},n.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),n.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})};var o={};(()=>{"use strict";function e(){document.querySelectorAll("[data-dropdown-trigger]").forEach((e=>{e.addEventListener("click",(t=>{t.preventDefault(),e.disabled||e.closest(".dropdown").classList.toggle("is-active")}))}))}function t(){document.querySelectorAll("[data-action-trigger]").forEach((e=>{const t=e.dataset.actionEvent||"click";e.addEventListener(t,(t=>{const n=null!==e.getAttribute("disabled"),o=e.classList.contains("is-selected");if(n||o)return;const c="select"===e.tagName.toLowerCase();c||t.preventDefault();const d=e.dataset.actionTrigger;let a="";a=c?e.value:e.dataset.actionValue,e.dataset.restoreScrollPos&&localStorage.setItem("scrollPosition",window.scrollY.toString());const s=e.closest("form"),i=e.dataset.actionFormUrl||"";i&&(s.action=i);let l=s.querySelector('input[name="action"]'),r=s.querySelector('input[name="action_value"]');l||(l=document.createElement("input"),l.type="hidden",l.name="action",s.appendChild(l)),r||(r=document.createElement("input"),r.type="hidden",r.name="action_value",s.appendChild(r)),l.value=d,r.value=a,s.dispatchEvent(new Event("submit",{bubbles:!0,cancelable:!0})),s.submit()}))})),window.addEventListener("load",(()=>{const e=localStorage.getItem("scrollPosition");null!==e&&(window.scrollTo(0,parseInt(e)),localStorage.removeItem("scrollPosition"))}))}function c(){function e(e){e.classList.remove("is-active")}document.querySelectorAll("[data-modal-trigger]").forEach((e=>{const t=e.dataset.modalTrigger,n=document.getElementById(t);e.addEventListener("click",(e=>{e.preventDefault(),function(e){e.classList.add("is-active");const t=e.querySelector(".has-select-all-on-show");t&&"function"==typeof t.select&&t.select()}(n)}))})),document.querySelectorAll(".modal-background, .modal-close, .modal-card-head .delete, .modal-close-button").forEach((t=>{const n=t.closest(".modal");t.addEventListener("click",(t=>{t.preventDefault(),e(n)}))})),document.addEventListener("keydown",(t=>{"Escape"===t.code&&document.querySelectorAll(".modal").forEach((t=>{e(t)}))}))}function d(){document.querySelectorAll("a[data-tab-page]").forEach((e=>{e.addEventListener("click",(t=>{e.closest("ul").querySelectorAll("li").forEach((e=>{e.classList.remove("is-active")})),e.closest("li").classList.add("is-active");const n=document.getElementById(e.dataset.tabPage);n.closest(".tabs-content").querySelectorAll(".tabs-page").forEach((e=>{e.classList.remove("is-active")})),n.classList.add("is-active");const o=e.closest(".tabs").querySelector('input[type="hidden"]');o&&(o.value=e.dataset.tabPage)}))}))}n.r(o),n.d(o,{BrowserDocument:()=>a,BrowserHelper:()=>s,activateActionButtonTriggers:()=>t,activateDropdownButtonTriggers:()=>e,activateModalOverlayTriggers:()=>c,activateTabTriggers:()=>d}),n(209);class a{constructor(e,t,n,o){this.index=e,this.name=t,this.parentIndex=n,this.isDocument=o,this.parent=null,this.children=[],this.checkbox=null,this.foldingHandle=null}}class s{constructor(e){this.documents=e,this.document_map={};for(const e of this.documents)this.document_map[e.index]=e,e.checkbox=document.getElementById(`node_${e.index}_checkbox`),e.index>0?(e.foldingHandle=document.getElementById(`node_${e.index}_unfolded`),e.foldingBox=document.getElementById(`node_${e.index}_folding_box`)):(e.foldingHandle=null,e.foldingBox=null);for(const e of this.documents)e.index>0&&(e.parent=this.document_map[e.parentIndex],e.parent.children.push(e));this.onNodeCheckboxClick=this.onNodeCheckboxClick.bind(this),this.onFoldingHandleChange=this.onFoldingHandleChange.bind(this)}addEventListeners(){for(const e of this.documents){const t=e.checkbox;t&&t.addEventListener("click",this.onNodeCheckboxClick);const n=e.foldingHandle;n&&n.addEventListener("change",this.onFoldingHandleChange)}const e=document.getElementById("browser_select_all");e&&e.addEventListener("click",(e=>{this.setNodeTreeChecked(0,!0),e.preventDefault()}));const t=document.getElementById("browser_select_none");t&&t.addEventListener("click",(e=>{this.setNodeTreeChecked(0,!1),e.preventDefault()}))}onNodeCheckboxClick(e){const t=e.target,n=parseInt(t.value);if(e.altKey)setTimeout((()=>{t.checked=!0}),10),this.setNodeTreeChecked(0,!1),this.onSelectCheckboxChanged(n,!0),e.preventDefault();else{const e=t.checked;this.onSelectCheckboxChanged(n,e)}}onFoldingHandleChange(e){const t=e.target,n=parseInt(t.value),o=t.checked;this.onUnfoldedCheckboxChanged(n,o)}onSelectCheckboxChanged(e,t){this.setNodeTreeChecked(e,t);let n=this.document_map[e].parent;for(;n;){let e=!1,t=!1;for(const o of n.children){if(o.checkbox.indeterminate){e=!0,t=!0;break}if(o.checkbox.checked){if(e=!0,t)break}else if(t=!0,e)break}e&&t?n.checkbox.indeterminate=!0:e?(n.checkbox.indeterminate=!1,n.checkbox.checked=!0):(n.checkbox.indeterminate=!1,n.checkbox.checked=!1),n=n.parent}this.updateSelectionCount()}setNodeTreeChecked(e,t){const n=this.document_map[e].checkbox;n.checked=t,n.indeterminate=!1;for(const n of this.document_map[e].children)this.setNodeTreeChecked(n.index,t)}updateSelectionCount(){let e=0;for(const t of this.documents)t.isDocument&&t.checkbox.checked&&(e+=1);document.getElementById("browser_select_count").innerText=e.toString()}onUnfoldedCheckboxChanged(e,t){const n=this.document_map[e].foldingBox;t?n.classList.remove("is-hidden"):n.classList.add("is-hidden")}}})(),design=o})();