import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getLeads } from '../api/GoogleSheetsClient';

function LeadList() {
  const [leads, setLeads] = useState([]);

  useEffect(() => {
    const fetchLeads = async () => {
      const data = await getLeads();
      setLeads(data);
    };
    fetchLeads();
  }, []);

  return (
    <div>
      <h1>WhatsApp Leads</h1>
      <ul>
        {leads.map(lead => (
          <li key={lead.id}>
            <Link to={`/lead/${lead.id}`}>{lead.phoneNumber}</Link>
            <span> - {lead.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default LeadList;