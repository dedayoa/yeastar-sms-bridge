<?php

/*+**********************************************************************************
 * The contents of this file are subject to the vtiger CRM Public License Version 1.0
 * ("License"); You may not use this file except in compliance with the License
 * The Original Code is: vtiger CRM Open Source
 * The Initial Developer of the Original Code is vtiger.
 * Portions created by vtiger are Copyright (C) vtiger.
 * All Rights Reserved.
 ************************************************************************************/

include_once 'vtlib/Vtiger/Net/Client.php';


class SMSNotifier_YeaSMS_Provider implements SMSNotifier_ISMSProvider_Model {
	
	private $username;
	private $password;
	private $parameters = array();
	
	const SERVICE_URI = 'https://yeasms-2.herokuapp.com/api/v1';
	
	private static $REQUIRED_PARAMETERS = array(
							array('name'=>'Token','label'=>'Auth Token','type'=>'text')
							);


	function __construct() {
		
	}	

	
	/**
	 * Function to get provider name
	 * @return <String> provider name
	 */
	public function getName() {
		return 'YeaSMS';
	}
	
	/**
	 * Function to get required parameters other than (userName, password)
	 * @return <array> required parameters list
	 */
	public function getRequiredParams() {
		return self::$REQUIRED_PARAMETERS;
	}
	
	/**
	 * Function to get service URL to use for a given type
	 * @param <String> $type like SEND, PING, QUERY
	 */
	public function getServiceURL($type = false) {
		if($type) {
			switch(strtoupper($type)) {
				case self::SERVICE_SEND: return self::SERVICE_URI . '/sms/text/simple/';
				case self::SERVICE_QUERY: return self::SERVICE_URI . '/sms/report/{mid}/';
			}
		}
		return false;
	}
	
	public function setAuthParameters($username, $password) {
		$this->username = $username;
		$this->password = $password;
	}
	
	/**
	 * Function to set non-auth parameter.
	 * @param <String> $key
	 * @param <String> $value
	 */
	public function setParameter($key, $value) {
		$this->parameters[$key] = $value;
	}

	/**
	 * Function to get parameter value
	 * @param <String> $key
	 * @param <String> $defaultValue
	 * @return <String> value/$default value
	 */
	public function getParameter($key, $defaultValue = false) {
		if(isset($this->parameters[$key])) {
			return $this->parameters[$key];
		}
		return $defaultValue;
	}
	
	/**
	 * Function to prepare parameters
	 * @return <Array> parameters
	 */
	protected function prepareParameters() {
		$params = array('username' => $this->username, 'password' => $this->password);
		foreach (self::$REQUIRED_PARAMETERS as $key=>$fieldInfo) {
			$params[$fieldInfo['name']] = $this->getParameter($fieldInfo['name']);
		}
		return $params;
	}
	
	public function send($message, $toNumbers) {
		
		if(!is_array($toNumbers)) {
			$toNumbers = array($toNumbers);
		}		
		
		$params = $this->prepareParameters();		
		$params['text'] = $message;
		
		$results = array();		
		$response = $this->sms($params, $toNumbers);
		$i = 0;
		
		foreach($response['messages'] as $mr) {
			$result = array();
			//array_push($results, $r);
			$result['id'] = $mr['messageId'];
			$result['to'] = $mr['to'];
			if ($mr['submitted'] == true){
				$result['status'] = self::MSG_STATUS_PROCESSING;
				$result['statusmessage'] = $mr['smsCount'].' message(s) submitted.';
			}			
			$results[] = $result;			
		}
		
		foreach($response['invalid_numbers'] as $failed) {
			$result = array();
			
			$result['error'] = true;
			$result['to'] = $failed;
			$result['statusmessage'] = 'Invalid Number. Message not submitted.';
			
			$results[] = $result;			
		}
		
		
		return $results;
	}
	
	
	public function sms($p, $mobile) {
		
		$data = array(
			"message" => $p["text"],
			"to" => $mobile
		);
		$data_string = json_encode($data);
		
		$ch = curl_init($this->getServiceURL(self::SERVICE_SEND));
		curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
		curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_HTTPHEADER, array(
			'Content-Type: application/json',
			'Content-Length: '. strlen($data_string),
			'Authorization: Token '.$p["Token"]
			)
		);
		
		for ($i = 0; $i < 3; $i++) {
			$response = curl_exec($ch);
			if (!($error = curl_error($ch))) {
				break;
			}
		};
		curl_close($ch);
		
		$result = json_decode($response, true);
		return $result;
		
	}
	
	public function query($messageid) {
		
		$params = $this->prepareParameters();
		$serviceURL = $this->getServiceURL(self::SERVICE_QUERY);
		$qurl = str_replace('{mid}', $messageid, $serviceURL);
		
		$httpClient = new Vtiger_Net_Client($qurl);
		$httpClient->setHeaders(array('Authorization' => 'Token '.$params["Token"], 'Content-Type' => 'application/json'));
		$response = $httpClient->doGet();
		
		$r = json_decode($response, true);
		$result = array();
		
		if ($r['sent'] == true){
			$result['status'] = self::MSG_STATUS_DISPATCHED ;
			$result['needlookup'] = 0;
			$result['statusmessage'] = 'Message successfully sent to ' . $r['to'] . ' on ' . $r['time'];
		}else if($r['error'] == true){
			$result['status'] = self::MSG_STATUS_ERROR;
			$result['needlookup'] = 1;
			$result['statusmessage'] = $r['errorReason'];
		}else if($r['failed'] == true){
		    $result['status'] = self::MSG_STATUS_FAILED;
		    $result['needlookup'] = 0;
		    $result['statusmessage'] = 'Message sending failed';
		}else{
			$result['status'] = self::MSG_STATUS_PROCESSING ;
			$result['needlookup'] = 1;
			$result['statusmessage'] = 'Message Processing';
		}
		
		return $result;
		
	}
}

?>