from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'newsdb')

coockies = {
    "consentUUID": "ce1ed1d2-84b6-4a7a-94d5-3484590d2054_46",
    "FTCookieConsentGDPR": "true"
}
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-UA,ru;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,en-US;q=0.5,en;q=0.4',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"23e94-l+9jDIGyHK2ESAqOTn+abWSfn5k"',
    'priority': 'u=0, i',
    'referer': 'https://www.ft.com/world?page=1',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    # 'cookie': 'FTClientSessionId=434474be-aced-438b-b418-b621c6c2dfa1; spoor-id=434474be-aced-438b-b418-b621c6c2dfa1; __exponea_etc__=66604c68-35b8-40ff-ae2e-19ff0640ad55; __exponea_time2__=-1.0547072887420654; consentUUID=47632738-eb6b-4c3c-a4f9-f2875fed7a84_46; consentDate=2025-07-31T07:42:36.382Z; usnatUUID=c727c362-4c5e-4d91-9f20-da5d66c8a048; FTCookieConsentGDPR=true; permutive-id=9c38ed4f-748e-4c66-94ba-5e97caa07dd3; next-edition=international; _gid=GA1.2.611640176.1753948025; _cb=CpsH7iCYaa19C0HVkI; zit.data.toexclude=0; _sxh=1733,; session=eyJjc3JmU2VjcmV0IjoiLWNnQmZISXdMaURhcDFwM1p5cHRCSVZJIn0=; session.sig=zlPiW3FdVh6n5-iWE9ojkAmtDdA; optimizelyEndUserId=oeu1753948035259r0.5313768334285766; ravelinDeviceId=rjs-300b1d1b-38a8-4335-b0a7-5ce79de2d2b4; _clck=1745v96%7C2%7Cfy2%7C0%7C2038; additionalInArticleSignupLanded=c1471ce7-0538-4cab-8c3d-3edfec8a8055; FTLogin=beta; ft_social_session_c=google; FTAllocation=83068592-0f6a-4091-b3c1-a2b9d94bac46; _gcl_au=1.1.981264970.1753948035.272113903.1753953793.1753953792; _ga=GA1.1.96406259.1753948025; FTConsent=behaviouraladsOnsite%3Aon%2CcookiesOnsite%3Aon%2CcookiesUseraccept%3Aon%2CdemographicadsOnsite%3Aon%2CenhancementByemail%3Aon%2CmarketingByemail%3Aon%2CpermutiveadsOnsite%3Aon%2CpersonalisedmarketingOnsite%3Aon%2CprogrammaticadsOnsite%3Aon; _csrf=9OIhJeuaJBrt1gFG5kOO3Urg; FTSession_s=04MGhZIPakCR07PBornZS6xG0wAAAZhgPfHTw8I.MEUCIEN97eU1LFaNr-UdzDjlCWLrP77OKU5ztVdSNegcMxQ8AiEA7MeTkywx3dv_ae3ef2pXrGiA18ixInbIY7Rt352utrg; FTCookieConsentSync=false; optimizelySession=1753961349595; _ga_6VD8DR7FRW=GS2.1.s1753961319$o2$g1$t1753961418$j60$l0$h576623180$dTl14JsPt2LVJxF4f9zN4-pm_CHEjeflgUw; ft-access-decision-policy=GRANTED_SUBX_REG_3_30; OriginalReferer=Direct; FtComEntryPoint=/content/6ae3cd28-b56b-4cd2-b4da-4c889e223f28; _cb_svref=https%3A%2F%2Fwww.ft.com%2Fworld%3Fpage%3D1; _fs_cd_cp_pRdRgnTnF68pCV2F=ASdwhCjMhKhJStP9NUIMXPq09AG9vPtsABHkOUyAWRmvfxi-_iUo4syyx0JDVOBWsIHFQSSGPUMRuz4C8ShVLfVBuwADbFgCuTvPsX7HOH3CxwK-qdRKPR7EEy75KIU7I6n1BLQbHc79viwvD-7TbhLPbTobndEH9a_ZRgBOVxANJPGzrTL51EaL; _chartbeat2=.1753948034662.1753966321441.1.KF-DFBKlVQklWhtkD-YMO4DLaQgH.2; _rdt_uuid=1753948035321.b0c2c1e8-8e06-401d-ac07-791fd11482d1; _uetsid=93d0e2e06de211f0a323f1f93dc19efc; _uetvid=93d0e3006de211f0b6d3e3d957e02000; _sanba=0; _sxo={"R":1,"tP":0,"tM":1,"sP":1,"sM":0,"dP":7,"dM":1,"dS":3,"tS":0,"cPs":80,"lPs":[1,1,1,20,1],"sSr":1,"sWids":[],"wN":0,"cdT":-3986691,"F":1,"RF":1,"w":0,"SFreq":3,"last_wid":0,"bid":1036,"accNo":"","clientId":"","isEmailAud":0,"isPanelAud":0,"hDW":0,"isRegAud":0,"isExAud":0,"isDropoff":0,"devT":1,"exPW":0,"Nba":-1,"userName":"","dataLayer":"","localSt":"","emailId":"","emailTag":"","subTag":"","lVd":"2025-7-31","oS":"434474be-aced-438b-b418-b621c6c2dfa1","cPu":"https://www.ft.com/content/6ae3cd28-b56b-4cd2-b4da-4c889e223f28","pspv":1,"pslv":40,"pssSr":20,"pswN":0,"psdS":2,"pscdT":-3986387,"RP":0,"TPrice":0,"ML":"","isReCaptchaOn":false,"reCaptchaSiteKey":"","reCaptchaSecretKey":"","extRefer":"","dM2":0,"tM2":0,"sM2":0,"RA":2,"ToBlock":-1,"CC":null,"groupName":null}; _clsk=1sqps1u%7C1753967763883%7C5%7C0%7Cb.clarity.ms%2Fcollect',
}

