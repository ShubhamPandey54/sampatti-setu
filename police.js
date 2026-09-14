const cases=[{id:"#SS-1025",item:"Mobile Phone",type:"Found",location:"Dwarka",date:"11 Sep 2026",status:"Pending"},{id:"#SS-1024",item:"Mobile Phone",type:"Lost",location:"Dwarka",date:"11 Sep 2026",status:"Pending"},{id:"#SS-1023",item:"Black Wallet",type:"Found",location:"Janakpuri",date:"11 Sep 2026",status:"Verified"},{id:"#SS-1022",item:"College ID Card",type:"Lost",location:"Uttam Nagar",date:"10 Sep 2026",status:"Matched"},{id:"#SS-1021",item:"Wrist Watch",type:"Found",location:"Dwarka",date:"10 Sep 2026",status:"Pending"},{id:"#SS-1018",item:"Black Wallet",type:"Lost",location:"Janakpuri",date:"09 Sep 2026",status:"Matched"}];
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
function showPage(id){$$(".page").forEach(p=>p.classList.toggle("active",p.id===id));$$(".nav-item").forEach(n=>n.classList.toggle("active",n.dataset.page===id));window.scrollTo({top:0,behavior:"smooth"})}
$$(".nav-item[data-page]").forEach(i=>i.addEventListener("click",()=>showPage(i.dataset.page)));
$$("[data-page-link]").forEach(b=>b.addEventListener("click",()=>showPage(b.dataset.pageLink)));
function statusHTML(s){return `<span class="status ${s.toLowerCase()}">${s}</span>`}
function renderRecent(){const c=$("#recentCases");if(!c)return;c.innerHTML=cases.slice(0,5).map(x=>`<tr><td><strong>${x.id}</strong></td><td>${x.item}</td><td><span class="status ${x.type.toLowerCase()}">${x.type}</span></td><td>${x.location}</td><td>${x.date}</td><td>${statusHTML(x.status)}</td></tr>`).join("")}
function renderCases(list=cases){const c=$("#casesTable");if(!c)return;if(!list.length){c.innerHTML=`<tr><td colspan="7" style="text-align:center;padding:30px;color:#718096">No cases found.</td></tr>`;return}c.innerHTML=list.map(x=>`<tr><td><strong>${x.id}</strong></td><td>${x.item}</td><td><span class="status ${x.type.toLowerCase()}">${x.type}</span></td><td>${x.location}</td><td>${x.date}</td><td>${statusHTML(x.status)}</td><td><button class="text-btn case-view" data-id="${x.id}">View</button></td></tr>`).join("");$$(".case-view").forEach(b=>b.addEventListener("click",()=>showToast("Case Details",`Opening ${b.dataset.id}`)))}
function filterCases(){const q=($("#caseSearch")?.value||"").toLowerCase().trim(),t=$("#typeFilter")?.value||"all",s=$("#statusFilter")?.value||"all";renderCases(cases.filter(x=>(x.id.toLowerCase().includes(q)||x.item.toLowerCase().includes(q)||x.location.toLowerCase().includes(q))&&(t==="all"||x.type===t)&&(s==="all"||x.status===s)))}
$("#caseSearch")?.addEventListener("input",filterCases);$("#typeFilter")?.addEventListener("change",filterCases);$("#statusFilter")?.addEventListener("change",filterCases);
const foundModal=$("#foundModal");function openFoundPopup(){foundModal?.classList.remove("hidden")}function closeFoundPopup(){foundModal?.classList.add("hidden")}
$("#closeModal")?.addEventListener("click",closeFoundPopup);$("#viewNotification")?.addEventListener("click",closeFoundPopup);$("#notificationBtn")?.addEventListener("click",openFoundPopup);foundModal?.addEventListener("click",e=>{if(e.target===foundModal)closeFoundPopup()});
$("#reviewMatch")?.addEventListener("click",()=>showPage("matching"));
$("#confirmMatch")?.addEventListener("click",()=>showToast("Match Confirmed","Cases #SS-1024 and #SS-1025 have been matched."));
$("#rejectMatch")?.addEventListener("click",()=>showToast("Match Rejected","The suggested match has been rejected."));
$$(".verify-btn").forEach(b=>b.addEventListener("click",()=>{const card=b.closest(".verification-card"),st=card?.querySelector(".status");if(st){st.textContent="Verified";st.className="status verified"}b.disabled=true;showToast("Case Verified","The found item has been successfully verified.")}));
$$(".reject-btn").forEach(b=>b.addEventListener("click",()=>{const card=b.closest(".verification-card");if(card)card.style.opacity=".55";showToast("Case Rejected","The verification request was rejected.")}));
function newCase(){showToast("New Case","New case form will open here.")}
$("#digitiseBtn")?.addEventListener("click",()=>{
    window.location.href="digitalization.html";
});
$("#newCaseBtn")?.addEventListener("click",newCase);$("#caseCreateBtn")?.addEventListener("click",newCase);
$("#logoutBtn")?.addEventListener("click",()=>showToast("Logout","Police portal logout action triggered."));
let toastTimer;function showToast(title,message){const t=$("#toast");if(!t)return;$("#toastTitle").textContent=title;$("#toastMessage").textContent=message;t.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove("show"),3000)}
renderRecent();renderCases();setTimeout(openFoundPopup,900);
