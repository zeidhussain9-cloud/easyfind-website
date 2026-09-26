import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getLead, updateLeadStatus } from '../api/GoogleSheetsClient';

function LeadDetail() {
  const { id } = useParams();
  const [lead, setLead] = useState(null);
  const [status, setStatus] = useState('');

  useEffect(() => {
    const fetchLead = async () => {
      const data = await getLead(id);
      setLead(data);
      setStatus(data.status);
    };
    fetchLead();
  }, [id]);

  const handleStatusChange = async (e) => {
    const newStatus = e.target.value;
    setStatus(newStatus);
    await updateLeadStatus(id, newStatus);
  };

  if (!lead) return <div>Loading...</div>;

  return (
    <div>
      <h1>Lead Details</h1>
      <p>Phone Number: {lead.phoneNumber}</p>
      <p>Message: {lead.message}</p>
      <p>Status: {lead.status}</p>
      <div>
        <label>Change Status: </label>
        <select value={status} onChange={handleStatusChange}>
          <option value="New">New</option>
          <option value="In Progress">In Progress</option>
          <option value="Converted">Converted</option>
          <option value="Pending Follow-up">Pending Follow-up</option>
        </select>
      </div>
      <a href={`https://wa.me/${lead.phoneNumber}`} target="_blank" rel="noopener noreferrer">Open WhatsApp</a>
    </div>
  );
}

export default LeadDetail;